from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.constraints import UniqueConstraint


# Create your models here.


class User(AbstractUser):
    online = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    belong = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opened_chats')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    UniqueConstraint(fields=('belong', 'to'), name='unique_person')

    def __str__(self):
        return self.belong.__str__() + "-" + self.target.__str__()


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    date = models.DateTimeField()
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    hasReached = models.BooleanField(default=False)
    hasRead = models.BooleanField(default=False)
    hasSent = models.BooleanField(default=True)

    def __str__(self):
        return self.source.__str__() + ": " + self.message + " to " + self.chat.__str__()