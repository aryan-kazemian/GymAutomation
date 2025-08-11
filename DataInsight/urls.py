from django.urls import path
from .views import ClubStatsListAPIView

urlpatterns = [
    path('club-stats/', ClubStatsListAPIView.as_view(), name='club-stats-list'),
]
