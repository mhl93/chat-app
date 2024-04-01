from rest_framework import serializers
from .models import Message, MGroup

# from user.serializers import UserSerializer

# from collections import OrderedDict


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ["id", "channel_id", "content", "created_at", "sender", "is_read"]


class MGroupSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = MGroup
        fields = ["id", "name", "created_at", "member", "messages", "creator"]
