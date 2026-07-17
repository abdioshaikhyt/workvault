"""
ASGI config for backend1 project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""
import uvloop
import asyncio
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend1.settings')

django_asgi_app = get_asgi_application()

from backend1app.routing import websocket_urlpatterns
from .middlewareJWTws import JWTAuthMiddlewareStackNoUser
from channels.security.websocket import AllowedHostsOriginValidator

application = ProtocolTypeRouter(
    {
        'http': django_asgi_app,
        'websocket': AllowedHostsOriginValidator(
            JWTAuthMiddlewareStackNoUser(
            URLRouter(websocket_urlpatterns)
            )
        ),
    }
)