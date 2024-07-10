from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Chat, Message
import json
import redis

r = redis.Redis(host='localhost', port=6379)


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.chat_id = None

    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]

        await self.channel_layer.group_add(self.chat_id, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.chat_id, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data["type"]

        if message_type == "chat_message":
            message = await self.create_message(data["source_id"], data["message"])

            await self.channel_layer.group_send(self.chat_id, {"type": "chat_message", "source_id": message.source_id,
                                                               "message": message.message,
                                                               "date": message.date.__str__(),
                                                               "message_id": message.id,
                                                               "has_reached": message.has_reached,
                                                               "has_read": message.has_read, "chat_id":
                                                                   message.chat_id, "has_sent": message.has_sent}
                                                )
        elif message_type == "chat_file":
            message = await self.create_file_message(data["source_id"], data["message"], data["file_name"])

            await self.channel_layer.group_send(self.chat_id, {"type": "chat_file", "source_id": message.source_id,
                                                               "message": message.message,
                                                               "date": message.date.__str__(),
                                                               "message_id": message.id,
                                                               "has_reached": message.has_reached,
                                                               "has_read": message.has_read, "chat_id":
                                                                   message.chat_id, "has_sent": message.has_sent,
                                                               "file_name": message.file_name}
                                                )
        elif message_type == "message_reached":
            await self.update_reached(data["message_id"], True)

            await self.channel_layer.group_send(self.chat_id, {"type": message_type, "message_id": data["message_id"]})
        elif message_type == "message_read":
            await self.update_read(data["message_id"], True)

            await self.channel_layer.group_send(self.chat_id, {"type": message_type, "message_id": data["message_id"]})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_file(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_read(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_reached(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_message(self, source_id, message):
        date = timezone.now()
        message = Message.objects.create(source=get_user_model().objects.get(id=source_id),
                                         message=message, date=date, chat=Chat.objects.get(id=self.chat_id))

        return message

    @database_sync_to_async
    def create_file_message(self, source_id, message, file_name):
        date = timezone.now()
        message = Message.objects.create(source=get_user_model().objects.get(id=source_id),
                                         message=message, date=date, chat=Chat.objects.get(id=self.chat_id), file_name=file_name)

        return message

    @database_sync_to_async
    def update_read(self, message_id, boolean):
        msg = Message.objects.get(id=message_id)
        msg.has_read = boolean
        msg.save()

        return msg

    @database_sync_to_async
    def update_reached(self, message_id, boolean):
        msg = Message.objects.get(id=message_id)
        msg.has_reached = boolean
        msg.save()

        return msg


class UserConsumer(AsyncWebsocketConsumer):

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.username = None

    async def connect(self):
        self.username = self.scope["url_route"]["kwargs"]["username"]

        await self.accept()

        await self.channel_layer.group_add(self.username, self.channel_name)

        if self.username == self.scope["user"].username:
            await self.update_online(True)

            await self.channel_layer.group_send(self.username, {"type": "is_online", "value": True})

    async def disconnect(self, close_code):
        if self.username == self.scope["user"].username:
            await self.update_online(False)
            await self.channel_layer.group_send(self.username, {"type": "is_online", "value": False})

        await self.channel_layer.group_discard(self.username, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "chat_creation":
            source_username = data["source_username"]
            chat_id = data["chat_id"]
            await self.channel_layer.group_send(
                self.username, {"type": "chat_creation", "source_username": source_username, "chat_id": chat_id}
            )
        elif data["type"] == "chat_creation_ack":
            source_username = data["source_username"]
            chat_id = data["chat_id"]
            await self.channel_layer.group_send(
                self.username, {"type": "chat_creation_ack", "chat_id": chat_id, "source_username": source_username}
            )
        elif data["type"] == "is_online":
            await self.channel_layer.group_send(
                self.username, {"type": "is_online", "value": await self.get_online()}
            )

    async def chat_creation(self, event):
        source_username = event["source_username"]
        chat_id = event["chat_id"]
        message_type = event["type"]

        await self.send(
            text_data=json.dumps({"type": message_type, "source_username": source_username, "chat_id": chat_id})
        )

    async def chat_creation_ack(self, event):
        await self.send(text_data=json.dumps(
            {"type": event["type"], "chat_id": event["chat_id"], "source_username": event["source_username"]}))

    async def is_online(self, event):
        await self.send(text_data=json.dumps({"type": event["type"], "value": event["value"]}))

    @database_sync_to_async
    def update_online(self, boolean):
        return get_user_model().objects.filter(username=self.username).update(online=boolean)

    @database_sync_to_async
    def get_online(self):
        return list(get_user_model().objects.filter(username=self.username).values('online'))[0]["online"]
