from django.urls import path
from .views import DynamicAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
]
