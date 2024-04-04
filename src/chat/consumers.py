from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from rest_framework.authtoken.models import Token
import json
from .models import MGroup, Message
from notifications.utils import send_notification
import redis
from asgiref.sync import sync_to_async

User = get_user_model()
redis_conn = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Handles WebSocket connections for chat features, including managing message sending, receiving, and marking messages as read.
    """

    async def connect(self):
        """
        Handles the initial WebSocket connection, authenticates the user,
        and subscribes the connection to the appropriate chat group.
        Processes any unread messages for the user upon connection.
        """

        self.channel_id = self.scope["url_route"]["kwargs"]["channel_id"]
        query_string = parse_qs(self.scope["query_string"].decode("utf8"))
        token_key = query_string.get("token", [None])[0]
        self.user = await self.get_user_from_token(token_key)
        if (
            isinstance(self.user, AnonymousUser)
            or not await self.is_mgroup_valid(self.channel_id)
            or not await self.is_user_member_of_group(self.user, self.channel_id)
        ):
            await self.close(code=403)
            return

        self.group_name = f"chat_{self.channel_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.process_unread_messages()

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        """
        Retrieves the user associated with a given authentication token.

        :param token_key: The authentication token key.
        :return: The user if the token is valid, otherwise AnonymousUser.
        """
        if token_key is None:
            return AnonymousUser()
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()

    @database_sync_to_async
    def is_mgroup_valid(self, channel_id):
        """
        Checks if a message group (chat room) exists for the given ID.

        :param channel_id: The ID of the chat group to check.
        :return: True if the group exists, False otherwise.
        """
        return MGroup.objects.filter(id=channel_id).exists()

    @database_sync_to_async
    def is_user_member_of_group(self, user, channel_id):
        """
        Determines if the specified user is a member of the given chat group.

        :param user: The user to check membership for.
        :param channel_id: The ID of the chat group.
        :return: True if the user is a member, False otherwise.
        """
        if user.is_authenticated:
            return MGroup.objects.filter(id=channel_id, member=user).exists()
        return False

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection by unsubscribing the connection from
        its chat group.
        """
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Processes messages received over the WebSocket. Handles different
        types of messages, such as chat messages or message read acknowledgments.

        :text_data: The JSON string of the received WebSocket message.
        """

        data = json.loads(text_data)
        message_type = data.get("type")

        if message_type == "chat_message":
            await self.process_message(data.get("message"))
        elif message_type == "acknowledge_message":
            await self.process_unread_messages()

    async def process_unread_messages(self):
        """
        Processes unread messages for the user, marking them as read if appropriate
        and notifying other group members.
        """

        key = f"unread_messages:{self.channel_id}:{self.user.id}"
        unread_message_ids = await sync_to_async(redis_conn.smembers)(key)
        for msg_id in unread_message_ids:
            await sync_to_async(redis_conn.srem)(key, msg_id)

            if not await self.is_message_unread_by_others(msg_id):
                await self.mark_message_as_read_in_db(msg_id)
                await self.notify_message_read_by_all(msg_id)

    async def save_unread_message_to_redis(self, message_obj):
        """
        Marks a new message as unread for all recipients except the sender,
        storing this information in Redis.

        :param message_obj: The message object that was sent.
        """
        channel_members = await self.get_group_members()
        for member_id in channel_members:
            if member_id != message_obj.sender_id:
                redis_key = f"unread_messages:{self.channel_id}:{member_id}"
                await database_sync_to_async(redis_conn.sadd)(redis_key, message_obj.id)

    @database_sync_to_async
    def get_group_members(self):
        """
        Retrieves all member IDs of the chat group associated with this consumer.

        :return: A list of user IDs who are members of the chat group.
        """
        group = MGroup.objects.get(id=self.channel_id)
        return [member.id for member in group.member.all()]

    @database_sync_to_async
    def is_message_unread_by_others(self, message_id):
        """
        Checks if a message is still marked as unread by any other user in the chat group.

        :param message_id: The ID of the message to check.
        :return: True if the message is unread by others, False otherwise.
        """
        channel_members = MGroup.objects.get(id=self.channel_id).member.all()
        for member in channel_members:
            if member.id != self.user.id and redis_conn.sismember(
                f"unread_messages:{self.channel_id}:{member.id}", message_id
            ):
                return True
        return False

    @database_sync_to_async
    def mark_message_as_read_in_db(self, message_id):
        """
        Marks a message as read in the database.

        :param message_id: The ID of the message to mark as read.
        """
        Message.objects.filter(id=message_id).update(is_read=True)

    async def notify_message_read_by_all(self, message_id):
        """
        Notifies the chat group that a message has been read by all members.

        :param message_id: The ID of the message that was read.
        """
        message = await database_sync_to_async(Message.objects.get)(id=message_id)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "message_read",
                "message_id": message_id,
                "sender_id": message.sender.id,
            },
        )

    async def message_read(self, event):
        """
        Sends a notification to the WebSocket that a message has been read by all recipients.

        :param event: The event dictionary containing message details.
        """

        message_id = event["message_id"]
        sender_id = event["sender_id"]

        await self.send(
            text_data=json.dumps(
                {
                    "type": "message_read",
                    "message_id": message_id,
                    "sender_id": sender_id,
                    "info": "Your message has been read by all recipients.",
                }
            )
        )

    async def chat_message(self, event):
        """
        Sends a chat message to the WebSocket.

        :param event: The event dictionary containing message details.
        """

        message = event["message"]
        message_id = event["message_id"]
        await self.send(
            text_data=json.dumps(
                {
                    "type": "chat_message",
                    "message": message,
                    "message_id": message_id,
                }
            )
        )

    async def process_message(self, message):
        """
        Processes and broadcasts a chat message to the group, marks it as unread for
        recipients, and sends notifications.

        :param message: The message content to process.
        """

        message_obj = await self.save_new_message(message)
        await self.broadcast_message(message_obj)
        await self.save_unread_message_to_redis(message_obj)
        await self.send_notifications(message_obj)

    @database_sync_to_async
    def save_new_message(self, message):
        """
        Saves a new message to the database.

        :param message: The message content to save.
        :return: The message object that was created.
        """

        channel = MGroup.objects.get(id=self.channel_id)
        return Message.objects.create(
            sender=self.user, content=message, channel_id=channel
        )

    async def broadcast_message(self, message_obj):
        """
        Broadcasts a message to all members of the chat group.

        :param message_obj: The message object to broadcast.
        """

        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "message": message_obj.content,
                "message_id": message_obj.id,
            },
        )

    async def send_notifications(self, message_obj):
        """
        Sends notifications to all members of the chat group, excluding the sender,
        about the new message.

        :param message_obj: The message object for which notifications should be sent.
        """

        channel = MGroup.objects.get(id=self.channel_id)
        for member in channel.member.all():
            if member != self.user:
                send_notification(
                    user=member,
                    message_received=message_obj.content,
                    message_sender=self.user,
                )
