from django.urls import path
from .views import UserAPIView, GymUserAPIView, GymUserPaymentAPIView, LogsAPIView
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    # Your existing API endpoints
    path('api/user/', UserAPIView.as_view(), name='user-api'),
    path('api/gym-user/', GymUserAPIView.as_view(), name='gym-user-api'),
    path('api/payment/', GymUserPaymentAPIView.as_view(), name='gym-user-payment-api'),
    path('api/logs/', LogsAPIView.as_view(), name='logs-api'),

    # Token endpoints for JWT authentication
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
