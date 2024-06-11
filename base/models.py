from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Person (User):

    def __str__(self):
        return self.username


class Chat (models.Model):
    id = models.IntegerField(primary_key=True)
    belong = models.ManyToManyField(User)

    def __str__(self):
        return self.belong.__str__()


class Message (models.Model):
    id = models.IntegerField(primary_key=True)
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    def __str__(self):
        return self.message
