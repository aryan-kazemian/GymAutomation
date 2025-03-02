from django.urls import path
from .views import UserAPIView, GymUserAPIView, GymUserPaymentAPIView


urlpatterns = [
    path('api/user/', UserAPIView.as_view(), name='user-api'),
    path('api/gym-user/', GymUserAPIView.as_view(), name='gym-user-api'),
    path('api/payment/', GymUserPaymentAPIView.as_view(), name='gym-user-payment-api'),

]