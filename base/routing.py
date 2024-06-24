from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"base/user/(?P<username>\w+)/$", consumers.UserConsumer.as_asgi()),
    re_path(r"base/chat/(?P<chat_id>\w+)/$", consumers.ChatConsumer.as_asgi()),
]