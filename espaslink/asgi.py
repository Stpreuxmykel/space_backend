import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import linkapp.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'espaslink.settings')
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            linkapp.routing.websocket_urlpatterns
        )
    ),
})
