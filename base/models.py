from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.constraints import UniqueConstraint


# Create your models here.


class User(AbstractUser):
    online = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Chat(models.Model):
    users = models.ManyToManyField(User, related_name='users')
    name = models.CharField(max_length=120, null=True, blank=True)
    def __str__(self):
        return ", ".join(str(user) for user in self.users.all())


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
