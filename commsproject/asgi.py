"""
ASGI config for commsproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.contrib.auth import get_user_model
from django.core.asgi import get_asgi_application
import base.routing
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'commsproject.settings')
django.setup()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(base.routing.websocket_urlpatterns))),
})

get_user_model().objects.filter(online=True).update(online=False)
