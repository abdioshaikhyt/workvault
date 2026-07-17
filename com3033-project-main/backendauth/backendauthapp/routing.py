
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/users/$', consumers.UserConsumer.as_asgi()),
    re_path(r'^ws/currentuser/$', consumers.CurrentUserConsumer.as_asgi()), 
]