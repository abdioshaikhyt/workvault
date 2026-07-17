
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class UserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("users", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("users", self.channel_name)

    async def user_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))
    
    async def practice_update(self, event):
        print("Websocket sending practice_update:", event["data"])
        await self.send(text_data=json.dumps(event["data"]))

class CurrentUserConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        print(f"{user} from token")
        self.group_name = f"user_{user.id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        print(f"[CurrentUserConsumer] Joined group 'currentusers'")

    async def disconnect(self, close_code):
        # Defensive check
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def force_logout(self, event):
        print(f"[CurrentUserConsumer] Received force_logout event: {event}")
        await self.send(text_data=json.dumps({
            "type": "force_logout",
            "message": event.get("message", "You have been logged out."),
            "user_id": event.get("user_id"),
        }))