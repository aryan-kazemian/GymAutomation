from django.urls import path
from .views import PaymentAPIView, PaymentSummaryAPIView

urlpatterns = [
    path('', PaymentAPIView.as_view()),
    path('single-payment-summary/', PaymentSummaryAPIView.as_view(), name='payment-summary'),
]
