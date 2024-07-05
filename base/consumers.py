from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Chat, Message
import json
import redis

r = redis.Redis(host='localhost', port=6379)


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None

    def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]

        async_to_sync(self.channel_layer.group_add)(
            self.chat_id, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chat_id, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        date = timezone.now()
        message_type = data["type"]

        if message_type == "chat_message":
            message = Message.objects.create(source=get_user_model().objects.get(id=data["source_id"]),
                                             message=data["message"], date=date, chat=Chat.objects.get(id=self.chat_id))
            message.save()

            async_to_sync(self.channel_layer.group_send)(self.chat_id,
                                                         {"type": "chat_message", "source_id": message.source_id,
                                                          "message": message.message,
                                                          "date": date.__str__(),
                                                          "message_id": message.id, "hasReached": message.hasReached,
                                                          "hasRead": message.hasRead, "chat_id":
                                                              message.chat_id, "hasSent": message.hasSent}
                                                         )
        elif message_type == "message_reached":
            msg = Message.objects.get(id=data["message_id"])
            msg.hasReached = True
            msg.save()

            async_to_sync(self.channel_layer.group_send)(self.chat_id,
                                                         {"type": message_type, "message_id": data["message_id"]}
                                                         )
        elif message_type == "message_read":
            msg = Message.objects.get(id=data["message_id"])
            msg.hasRead = True
            msg.save()

            async_to_sync(self.channel_layer.group_send)(self.chat_id,
                                                         {"type": message_type, "message_id": data["message_id"]}
                                                         )

    def chat_message(self, event):
        self.send(text_data=json.dumps(event))

    def message_read(self, event):
        self.send(text_data=json.dumps(event))

    def message_reached(self, event):
        self.send(text_data=json.dumps(event))


class UserConsumer(WebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.username = None

    def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        self.accept()

        if self.username == self.scope["user"].username:
            get_user_model().objects.filter(username=self.username).update(online=True)

            async_to_sync(self.channel_layer.group_send)(self.username, {"type": "is_online", "value": True})

        async_to_sync(self.channel_layer.group_add)(self.username, self.channel_name)

    def disconnect(self, close_code):
        if self.username == self.scope["user"].username:
            get_user_model().objects.filter(username=self.username).update(online=False)

            async_to_sync(self.channel_layer.group_send)(self.username, {"type": "is_online", "value": False})

        async_to_sync(self.channel_layer.group_discard)(self.username, self.channel_name)

    def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data["type"]

        if message_type == "chat_creation" or message_type == "chat_creation_ack":
            async_to_sync(self.channel_layer.group_send)(self.username, {"type": message_type,
                                                                         "source_username": data["source_username"],
                                                                         "chat_id": data["chat_id"]})
        elif message_type == "is_online":
            async_to_sync(self.channel_layer.group_send)(self.username, {"type": message_type,
                                                                         "value": list(get_user_model().objects.filter
                                                                                       (username=self.username).values(
                                                                             'online'))[0]["online"]})

    def chat_creation(self, event):
        self.send(text_data=json.dumps(event))

    def chat_creation_ack(self, event):
        self.send(text_data=json.dumps(event))

    def is_online(self, event):
        self.send(text_data=json.dumps(event))
