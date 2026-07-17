"""
ASGI config for backendauth project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backendauth.settings')

django_asgi_app = get_asgi_application()                   

from backendauthapp.routing import websocket_urlpatterns               
from .middlewareJWTws import JWTAuthMiddlewareStack                     
from channels.security.websocket import AllowedHostsOriginValidator      

application = ProtocolTypeRouter(                           
    {                                                            
        'http': django_asgi_app,                                
        'websocket': AllowedHostsOriginValidator(          
            JWTAuthMiddlewareStack(                  
            URLRouter(websocket_urlpatterns)               
            )                                       
        ),                                      
    }                                             
) 