from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.constraints import UniqueConstraint


# Create your models here.


class User(AbstractUser):
    online = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Chat(models.Model):
    belong = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opened_chats')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')

    class Meta:
        constraints = [
            UniqueConstraint(fields=['belong', 'target'], name='unique_chat'),
        ]

    def __str__(self):
        return self.belong.__str__() + "-" + self.target.__str__()


class Message(models.Model):
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    date = models.DateTimeField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    has_reached = models.BooleanField(default=False)
    has_read = models.BooleanField(default=False)
    has_sent = models.BooleanField(default=True)
    file_name = models.TextField(default=False)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return self.source.__str__() + ": " + self.message + " to " + self.chat.__str__()
