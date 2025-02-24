from django.urls import path
from .views import GymUserAPIView, GymUserPaymentSerializerAPIView, UserLoginView, UserSerializerAPIView

urlpatterns = [
    path('api/gym-user/', GymUserAPIView.as_view(), name='gym-user-api'),
    path('api/gym-user-payment/', GymUserPaymentSerializerAPIView.as_view(), name='gym-user-payment-api'),
    path('api/login/', UserLoginView.as_view(), name='user-login-api'),
    path('api/user/', UserSerializerAPIView.as_view(), name='user-api'),

]
