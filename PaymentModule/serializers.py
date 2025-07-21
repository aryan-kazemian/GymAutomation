from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class PaymentSummarySerializer(serializers.Serializer):
    total_price = serializers.IntegerField()
    year_price = serializers.IntegerField()
    month_price = serializers.IntegerField()
    today_price = serializers.IntegerField()
    daily_prices = serializers.DictField(child=serializers.IntegerField())
    monthly_prices = serializers.DictField(child=serializers.IntegerField())
