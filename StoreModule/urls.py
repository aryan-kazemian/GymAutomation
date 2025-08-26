from django.urls import path
from .views import (
    StoreConfigurationAPIView,
    CategoryAPIView,
    ProductAPIView,
    OrderAPIView,
)

urlpatterns = [
    path("stores/", StoreConfigurationAPIView.as_view()),
    path("categories/", CategoryAPIView.as_view()),
    path("products/", ProductAPIView.as_view()),
    path("orders/", OrderAPIView.as_view()),
]
