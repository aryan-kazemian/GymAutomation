from rest_framework import serializers
from .models import User, GymUser, GymUserPayment, Logs, VipLocker


class UserSerializer(serializers.ModelSerializer):
    vip_locker_numbers = serializers.PrimaryKeyRelatedField(
        many=True, queryset=VipLocker.objects.all(), required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'last_login', 'is_active',
            'date_joined', 'use_day_left', 'gym_name', 'gym_address',
            'phone_number', 'expiration_date', 'locker_count', 'vip_locker_count',
            'vip_locker_numbers', 'image'
        ]
        read_only_fields = ['id', 'username', 'last_login', 'date_joined', 'is_active', 'expiration_date']


class GymUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = '__all__'

class GymUserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUser
        fields = ['name', 'family', 'email', 'nation_cod', 'phone_number', 'birthday',
                  'fingerprint', 'face_image', 'is_staff', 'user_state', 'locker_number', 'face_binary', 'biometric_type',
                  "started_payment_date"
                  ]

class GymUserPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUserPayment
        fields = '__all__'
        read_only_fields = ['id', 'payed_date']

class GymUserPaymentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = GymUserPayment
        fields = ['payed_amount', 'subscription_duration', 'subscription_days', 'payment_method', 'payment_state']

class LogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = '__all__'

class LogsEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logs
        fields = ['logout_time']

class VipLockerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VipLocker
        fields = ['id', 'number']
