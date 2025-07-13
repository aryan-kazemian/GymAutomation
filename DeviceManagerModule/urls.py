from django.urls import path
from .views import DeviceAPIView

urlpatterns = [
    path('', DeviceAPIView.as_view(), name='device-api'),
]
