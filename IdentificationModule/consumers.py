# IdentificationModule/consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class IdentificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join group for sending events
        await self.channel_layer.group_add("identification_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard("identification_group", self.channel_name)

    async def identification_event(self, event):
        # Receive event from group and send to WebSocket
        await self.send(text_data=json.dumps({
            "data": event["data"]
        }))
