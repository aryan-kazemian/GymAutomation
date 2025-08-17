from django.urls import path
from .views import DynamicAPIView, SportAPIView, CoachManagementAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
    path('sport/', SportAPIView.as_view(), name='sport-api'),
    path('coach-management/', CoachManagementAPIView.as_view(), name='coach-management')
]
