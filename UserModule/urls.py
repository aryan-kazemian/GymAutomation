from django.urls import path
from .views import DynamicAPIView, SportAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
    path('sport/', SportAPIView.as_view(), name='sport-api'),
]
