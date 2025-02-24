from rest_framework import serializers
from .models import GymUser, GymUserPayment, User

class GymUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = '__all__'

class GymUserPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUserPayment
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'last_login', 'is_active', 'date_joined', 'use_day_left',  'gym_name', 'gym_address', 'phone_number', 'expiration_date', 'use_day_left', 'locker_count', 'vip_locker_count', 'image']

