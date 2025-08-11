from rest_framework import serializers
from .models import ClubStats

class ClubStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubStats
        fields = '__all__'
