# linkapp/routing.py
from django.urls import re_path
from . import consumers  # Ensure this imports your WebSocket consumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),  # Adjust the regex as necessary
]
