from django.db import models
import uuid
from user.models import User

# Create your models here.


class MGroup(models.Model):
    class GroupCategory(models.TextChoices):
        PUBLIC = "Public", "Public"
        PRIVATE = "Private", "Private"

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    member = models.ManyToManyField(User, related_name="mgroups")
    creator = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="created_mgroups"
    )
    category = models.CharField(
        max_length=20,
        choices=GroupCategory.choices,
        default=GroupCategory.PRIVATE,
    )

    def __str__(self):
        return str(self.id)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    channel_id = models.ForeignKey(
        MGroup, on_delete=models.CASCADE, null=True, related_name="messages"
    )
    content = models.CharField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.content
