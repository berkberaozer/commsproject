from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Chat, Message, Status
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
            message = await self.create_message(data["source_username"], data["message"])

            await self.channel_layer.group_send(self.chat_id, {"type": "chat_message",
                                                               "source_username": message.source.username,
                                                               "message": message.message,
                                                               "date": message.date.__str__(),
                                                               "message_id": message.id,
                                                               "statuses": await self.get_statuses(message),
                                                               "chat_id": message.chat_id,
                                                               "has_sent": message.has_sent})
        elif message_type == "chat_file":
            message = await self.create_file_message(data["source_username"], data["message"], data["file_name"])

            await self.channel_layer.group_send(self.chat_id, {"type": "chat_file",
                                                               "source_username": data["source_username"],
                                                               "message": message.message,
                                                               "date": message.date.__str__(),
                                                               "message_id": message.id,
                                                               "statuses": await self.get_statuses(message),
                                                               "chat_id": message.chat_id,
                                                               "has_sent": message.has_sent,
                                                               "file_name": message.file_name})
        elif message_type == "message_reached":
            await self.update_reached(data["message_id"], data["user_id"], True)

            await self.channel_layer.group_send(self.chat_id, {"type": message_type, "message_id": data["message_id"],
                                                               "user_id": data["user_id"]})
        elif message_type == "message_read":
            await self.update_read(data["message_id"], data["user_id"], True)

            await self.channel_layer.group_send(self.chat_id, {"type": message_type, "message_id": data["message_id"],
                                                               "user_id": data["user_id"]})
        elif message_type == "call_request":
            await self.channel_layer.group_send(self.chat_id, {"type": "call_request",
                                                               "source_username": data["source_username"],
                                                               "message": data["message"]})
        elif message_type == "call_ack":
            await self.channel_layer.group_send(self.chat_id, {"type": "call_ack",
                                                               "source_username": data["source_username"],
                                                               "message": data["message"]})
        elif message_type == "new_ice_candidate":
            await self.channel_layer.group_send(self.chat_id, {"type": "new_ice_candidate", "message": data["message"]})
        elif message_type == "call_hangup":
            await self.channel_layer.group_send(self.chat_id, {"type": "call_hangup"})

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_file(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_read(self, event):
        await self.send(text_data=json.dumps(event))

    async def message_reached(self, event):
        await self.send(text_data=json.dumps(event))

    async def all_reached(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_request(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_ack(self, event):
        await self.send(text_data=json.dumps(event))

    async def call_hangup(self, event):
        await self.send(text_data=json.dumps(event))

    async def new_ice_candidate(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def create_message(self, source_username, message):
        date = timezone.now()
        source = get_user_model().objects.get(username=source_username)
        message = Message.objects.create(source=source, message=message,
                                         date=date, chat=Chat.objects.get(id=self.chat_id))

        # creates a status for each of the recipients
        for user in Chat.objects.get(id=self.chat_id).users.exclude(username=source_username).all():
            Status.objects.create(user=user, message=message)

        return message

    @database_sync_to_async
    def create_file_message(self, source_username, message, file_name):
        date = timezone.now()
        source = get_user_model().objects.get(username=source_username)
        message = Message.objects.create(source=source, message=message, date=date,
                                         chat=Chat.objects.get(id=self.chat_id), file_name=file_name)

        # creates a status for each of the recipients
        for user in Chat.objects.get(id=self.chat_id).users.exclude(username=source_username).all():
            Status.objects.create(user=user, message=message)

        return message

    @database_sync_to_async
    def update_read(self, message_id, user_id, boolean):
        status = Status.objects.filter(message_id=message_id, user_id=user_id)[0]
        status.has_read = boolean
        status.save()

        return status

    @database_sync_to_async
    def update_reached(self, message_id, user_id, boolean):
        status = Status.objects.filter(message_id=message_id, user_id=user_id)[0]
        status.has_reached = boolean
        status.save()

        return status

    @database_sync_to_async
    def get_statuses(self, message):
        return list(message.statuses.all().values())


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
        elif data["type"] == "group_creation":
            await self.channel_layer.group_send(
                self.username, {"type": "group_creation",
                                "chat_id": data["chat_id"],
                                "name": data["name"],
                                "users": data["users"],
                                "source_username": data["source_username"]})

    async def chat_creation(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_creation_ack(self, event):
        await self.send(text_data=json.dumps(event))

    async def group_creation(self, event):
        await self.send(text_data=json.dumps(event))

    async def is_online(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def update_online(self, boolean):
        return get_user_model().objects.filter(username=self.username).update(online=boolean)

    @database_sync_to_async
    def get_online(self):
        return get_user_model().objects.filter(username=self.username).values('online')[0]["online"]
