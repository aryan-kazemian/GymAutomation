# IdentificationModule/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/identification/$', consumers.IdentificationConsumer.as_asgi()),
]
