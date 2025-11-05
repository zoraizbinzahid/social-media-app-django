import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['user'].id
        self.room_group_name = f'notifications_{self.user_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': event['type'],
            'message': event['message'],
            'notification_type': event['notification_type'],
            'sender_username': event.get('sender_username', ''),
            'post_id': event.get('post_id'),
            'created_at': event.get('created_at'),
            'unread_count': event.get('unread_count', 0)
        }))

class GlobalNotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'global_notifications'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from room group
    async def send_global_notification(self, event):
        await self.send(text_data=json.dumps({
            'type': 'global_notification',
            'message': event['message'],
            'notification_type': event['notification_type']
        }))