# serializers.py
from rest_framework import serializers
from .models import Payment


class CreateOrderSerializer(serializers.Serializer):
    orders = serializers.JSONField()
    coupon = serializers.CharField(required=False)


class PaymentSerializer(serializers.ModelSerializer):
    razorpay_order_id = serializers.CharField(required=True)
    razorpay_payment_id = serializers.CharField(required=True)
    razorpay_signature = serializers.CharField(required=True)

    class Meta:
        model = Payment
        fields = ['razorpay_order_id', 'razorpay_payment_id',
                  'razorpay_signature']


class PaymentSerializerForOrder(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
