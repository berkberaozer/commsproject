from django.db import models
from django.contrib.auth.models import User
from django.db.models.constraints import UniqueConstraint


# Create your models here.


class Person(User):
    def __str__(self):
        return self.__str__()


class Chat(models.Model):
    id = models.AutoField(primary_key=True)
    belong = models.ForeignKey(User, on_delete=models.CASCADE, related_name='opened_chats')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_chats')
    UniqueConstraint(fields=('belong', 'to'), name='unique_person')

    def __str__(self):
        return self.target.__str__()


class Message(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    def __str__(self):
        return self.message


class Group(models.Model):
    id = models.AutoField(primary_key=True)
    belong = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self):
        return self.belong.__str__()


class GroupMessage(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return self.message.__str__()
