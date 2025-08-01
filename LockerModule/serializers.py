from rest_framework import serializers
from .models import Locker, Saloon


class SaloonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Saloon
        fields = '__all__'

class LockerSerializer(serializers.ModelSerializer):
    locker_place_description = serializers.SerializerMethodField()

    class Meta:
        model = Locker
        fields = [field.name for field in Locker._meta.fields] + ['locker_place_description']

    def get_locker_place_description(self, obj):
        return obj.locker_place.description if obj.locker_place else None
