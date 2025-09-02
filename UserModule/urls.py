from django.urls import path
from .views import DynamicAPIView, SportAPIView, CoachManagementAPIView, CoachUsersAPIView, TestCoachUsersAPIView

urlpatterns = [
    path('dynamic/', DynamicAPIView.as_view()),
    path('sport/', SportAPIView.as_view(), name='sport-api'),
    path('coach-management/', CoachManagementAPIView.as_view(), name='coach-management'),
    path('coach-user-management/', TestCoachUsersAPIView.as_view(), name='coach-user-management')
]
