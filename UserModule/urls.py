from django.urls import path
from .views import DynamicAPIView, AuthenticationAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
    path('authentication/', AuthenticationAPIView.as_view())
]
