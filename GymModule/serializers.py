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


class UserSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']  # You can add more fields if needed.

    def update(self, instance, validated_data):
        # Here we update the instance with new values
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        # If you have a custom field like phone number or address, you can add them here
        instance.save()
        return instance
