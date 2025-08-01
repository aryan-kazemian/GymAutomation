from django.urls import path
from .views import LockerAPIView, SaloonAPIView

urlpatterns = [
    path('', LockerAPIView.as_view()),
    path('/saloon/', SaloonAPIView.as_view()),
]
