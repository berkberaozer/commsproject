import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.utils import timezone

from .models import User, Chat, Message
import redis

r = redis.StrictRedis(host='localhost', port=6379)


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
            message = Message.objects.create(source=User.objects.get(id=data["source_id"]), message=data["message"],
                                             date=date,
                                             chat=Chat.objects.get(id=self.chat_id))
            message.save()

            async_to_sync(self.channel_layer.group_send)(
                self.chat_id,
                {"type": "chat_message", "source_id": message.source_id, "message": message.message,
                 "date": date.__str__(),
                 "message_id": message.id, "hasReached": message.hasReached, "hasRead": message.hasRead, "chat_id":
                     message.chat_id, "hasSent": message.hasSent}
            )
        elif message_type == "message_reached":
            async_to_sync(self.channel_layer.group_send)(self.chat_id,
                                                         {"type": message_type, "message_id": data["message_id"]}
                                                         )

            msg = Message.objects.get(id=data["message_id"])
            msg.hasReached = True
            msg.save()

        elif message_type == "message_read":
            async_to_sync(self.channel_layer.group_send)(self.chat_id,
                                                         {"type": message_type, "message_id": data["message_id"]}
                                                         )

            msg = Message.objects.get(id=data["message_id"])
            msg.hasRead = True
            msg.save()

    def chat_message(self, event):
        self.send(text_data=json.dumps(
            {"type": event["type"], "source_id": event["source_id"], "message": event["message"],
             "date": event["date"],
             "chat_id": event["chat_id"], "message_id": event["message_id"], "hasReached": event["hasReached"],
             "hasRead": event["hasRead"],
             "hasSent": event["hasSent"]}))

    def message_read(self, event):
        self.send(text_data=json.dumps({"type": event["type"], "message_id": event["message_id"]}))

    def message_reached(self, event):
        self.send(text_data=json.dumps({"type": event["type"], "message_id": event["message_id"]}))


class UserConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.username = None

    def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]
        async_to_sync(self.channel_layer.group_add)(
            self.username, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.username, self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        source_username = data["source_username"]
        chat_id = data["chat_id"]

        async_to_sync(self.channel_layer.group_send)(
            self.username, {"type": "chat.creation", "source_username": source_username, "chat_id": chat_id}
        )

    def chat_creation(self, event):
        source_username = event["source_username"]
        chat_id = event["chat_id"]

        self.send(text_data=json.dumps({"source_username": source_username, "chat_id": chat_id}))
