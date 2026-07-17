import traceback
from urllib.parse import parse_qs
from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import decode as jwt_decode
from jwt import InvalidSignatureError, ExpiredSignatureError, DecodeError
from types import SimpleNamespace
from jwt import ExpiredSignatureError, InvalidSignatureError

class JWTAuthMiddlewareNoUser:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            token_list = parse_qs(scope["query_string"].decode("utf8")).get('token', None)
            if token_list:
                token = token_list[0]
                payload = jwt_decode(token, settings.SIMPLE_JWT["VERIFYING_KEY"], algorithms=["RS256"])
                # Create a simple user object from JWT claims
                user = SimpleNamespace(
                    id=payload.get("user_id"),
                    username=payload.get("username", ""),
                    is_authenticated=True
                )
                scope["user"] = user
            else:
                scope["user"] = AnonymousUser()
        except (ExpiredSignatureError, InvalidSignatureError):
            scope["user"] = AnonymousUser()
        except Exception:
            scope["user"] = AnonymousUser()

        return await self.app(scope, receive, send)

def JWTAuthMiddlewareStackNoUser(app):
    return JWTAuthMiddlewareNoUser(AuthMiddlewareStack(app))