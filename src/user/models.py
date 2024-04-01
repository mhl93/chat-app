from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    phone_number = models.CharField(max_length=11, null=True, blank=True)
    is_email_notif = models.BooleanField(default=False)
    is_push_notif = models.BooleanField(default=False)

    def __str__(self):
        return self.username
