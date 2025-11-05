import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message
from notifications.utils import create_notification

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

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

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        sender_id = text_data_json['sender_id']

        # Save message to database
        conversation = await self.get_conversation()
        sender = await self.get_user(sender_id)
        saved_message = await self.save_message(conversation, sender, message)

        # Get the other user in the conversation to send notification
        other_user = await self.get_other_user(conversation, sender)
        
        # Create notification for the other user
        if other_user:
            await self.create_message_notification(other_user, sender, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_id': sender_id,
                'sender_username': sender.username,
                'timestamp': saved_message.timestamp.isoformat(),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_conversation(self):
        return Conversation.objects.get(id=self.conversation_id)

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def save_message(self, conversation, sender, content):
        return Message.objects.create(
            conversation=conversation,
            sender=sender,
            content=content
        )

    @database_sync_to_async
    def get_other_user(self, conversation, current_user):
        """Get the other user in the conversation"""
        # Get all participants excluding the current user
        other_users = conversation.participants.exclude(id=current_user.id)
        return other_users.first()  # Return the first other user found

    @database_sync_to_async
    def create_message_notification(self, recipient, sender, message_content):
        """Create a notification for new messages"""
        try:
            # Truncate long messages for the notification
            if len(message_content) > 50:
                preview = message_content[:50] + '...'
            else:
                preview = message_content
                
            create_notification(
                recipient=recipient,
                notification_type='new_message',
                message=f"New message from {sender.username}: {preview}",
                sender=sender
            )
            print(f"Notification created for {recipient.username} from {sender.username}")
        except Exception as e:
            print(f"Error creating message notification: {e}")