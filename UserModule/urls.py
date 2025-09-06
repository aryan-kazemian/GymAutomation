from django.urls import path
from .views import DynamicAPIView, SportAPIView, CoachManagementAPIView, CoachUsersAPIView, FingerprintAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
    path('sport/', SportAPIView.as_view(), name='sport-api'),
    path('coach-management/', CoachManagementAPIView.as_view(), name='coach-management'),
    path('coach-user-management/', CoachUsersAPIView.as_view(), name='coach-user-management'),
    path('fingerprint/', FingerprintAPIView.as_view(), name='fingerprint'),
]
