from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/backend1/currentuser/$', consumers.UserJobsConsumer.as_asgi()), 
]