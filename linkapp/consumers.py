# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from linkapp.models import Room, Message, GoogleUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"User connected to room: {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"User disconnected from room: {self.room_name}")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        sender_id = self.scope['user'].id  # Assuming this is Django Auth user for now

        room = await self.get_room(self.room_name)

        # Depending on the type of the sender, fetch the right user model (User or GoogleUser)
        sender = await self.get_user(sender_id)

        await self.save_message(room, sender, message_content)

        # Broadcast the message to the room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'sender': sender_id
            }
        )
        print(f"Message received: {message_content} from user {sender_id}")

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @staticmethod
    async def get_room(room_name):
        return await Room.objects.get(room_name=room_name)

    @staticmethod
    async def get_user(user_id):
        try:
            # Try to fetch User first
            return await User.objects.get(id=user_id)
        except User.DoesNotExist:
            # If User is not found, fetch GoogleUser
            return await GoogleUser.objects.get(id=user_id)

    @staticmethod
    async def save_message(room, sender, message_content):
        if isinstance(sender, User):
            Message.objects.create(
                room=room,
                user_sender=sender,
                content=message_content
            )
        elif isinstance(sender, GoogleUser):
            Message.objects.create(
                room=room,
                google_sender=sender,
                content=message_content
            )
