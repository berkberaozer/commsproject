from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    online = models.BooleanField(default=False)
    public_key = models.TextField(null=True, blank=True)
    enc_private_key = models.TextField(null=True, blank=True)
    pass_phrase = models.TextField(null=False, blank=False)

    def __str__(self):
        return self.username


class Chat(models.Model):
    users = models.ManyToManyField(User, related_name='chats')
    name = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        if self.name:
            return "Group Chat " + self.name + "(Contains: " + ", ".join(str(user) for user in self.users.all()) + ")"
        else:
            return "Chat between " + " and ".join(str(user) for user in self.users.all())


class Message(models.Model):
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    targets = models.ManyToManyField(User, through="Status", related_name="received_messages")
    message = models.TextField()
    date = models.DateTimeField()
    has_sent = models.BooleanField(default=True)
    file_name = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return "Message from " + self.source.__str__() + " in the " + self.chat.__str__()


class Status(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="statuses")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    has_reached = models.BooleanField(default=False)
    has_read = models.BooleanField(default=False)

    class Meta:
        unique_together = (("message", "user"),)
        verbose_name_plural = "statuses"

    def __str__(self):
        return "Status of message " + self.message.source.__str__() + " to " + self.user.__str__() + " in " + self.message.chat.__str__()
