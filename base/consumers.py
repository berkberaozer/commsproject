import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import User, Chat, Message


class ChatConsumer(WebsocketConsumer):
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

        Message.objects.create(source=User.objects.get(id=data["source_id"]), message=data, date=date, chat=Chat.objects.get(id=self.chat_id))

    def chat_message(self, event):
        source_id = event["source_id"]
        message = event["message"]

        self.send(text_data=json.dumps({"source_id": source_id, "message": message}))
