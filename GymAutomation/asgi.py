import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import IdentificationModule.routing  # 👈 Add this import

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GymAutomation.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            IdentificationModule.routing.websocket_urlpatterns
        )
    ),
})
