import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User, Chat, Message


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
        source_id = data["source_id"]
        message = data["message"]
        date = datetime.now()

        async_to_sync(self.channel_layer.group_send)(
            self.chat_id, {"type": "chat.message", "source_id": source_id, "message": message, "date": date.__str__()}
        )

        Message.objects.create(source=User.objects.get(id=data["source_id"]), message=data["message"], date=date,
                               chat=Chat.objects.get(id=self.chat_id))

    def chat_message(self, event):
        source_id = event["source_id"]
        message = event["message"]

        self.send(text_data=json.dumps({"source_id": source_id, "message": message}))


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
            self.username, {"type": "chat.message", "source_username": source_username, "chat_id": chat_id}
        )

    def chat_message(self, event):
        source_username = event["source_username"]
        chat_id = event["chat_id"]

        self.send(text_data=json.dumps({"source_username": source_username, "chat_id": chat_id}))
