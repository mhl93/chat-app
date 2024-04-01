from django.core.mail import send_mail
from django.conf import settings


def send_notification(user, message_received, message_sender):
    if user.is_email_notif:
        send_email_notification(user.email, message_received, message_sender.username)

    if user.is_push_notif:
        send_push_notification(user, message_received, message_sender)


def send_email_notification(user_email, message_received, message_sender):
    SUBJECT = "You have a notification"
    BODY = f"A message '{message_received}' sent by {message_sender}"
    send_mail(
        SUBJECT,
        BODY,
        settings.DEFAULT_FROM_EMAIL,
        [user_email],
        fail_silently=False,
    )


def send_push_notification(token, title, body):
    pass
    # url = "https://fcm.googleapis.com/fcm/send"
    # server_key = "your_server_key_here"

    # headers = {
    #     "Content-Type": "application/json",
    #     "Authorization": "key=" + server_key,
    # }

    # payload = {
    #     "notification": {"title": title, "body": body},
    #     "to": token,
    # }

    # response = requests.post(url, headers=headers, data=json.dumps(payload))
