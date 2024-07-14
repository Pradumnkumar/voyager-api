# views.py
import razorpay
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from django.views.decorators.csrf import csrf_exempt

from .models import Payment, Coupon
from .serializers import (CreateOrderSerializer,
                          PaymentSerializer,
                          PaymentSerializerForOrder)

client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET)
    )
order_type = {
    'seminar': 99,
    'sector_assessment': 499
}


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self, **kwargs):
        return CreateOrderSerializer

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        # Get Orders and Coupon
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        # Calculate discount
        discount = 0
        products = validated_data['orders']
        coupon_code = validated_data.get('coupon', None)
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code)
                discount = coupon.discount
            except ObjectDoesNotExist:
                discount = 0

        price = sum([order_type[product] for product in products])
        price_after_discount = (1 - (discount/100)) * price
        order_data = {
            'amount': price_after_discount,
            'currency': 'INR',
            'orders': products
            }
        order = CreateOrderSerializer(data=order_data)
        order.is_valid(raise_exception=True)

        razorpay_data = {
            'amount': int(price_after_discount * 100),
            'currency': 'INR',
            'payment_capture': '1'
            }
        payment = client.order.create(razorpay_data)
        payment_data = {
            'user': request.user.id,
            'razorpay_order_id': payment['id'],
            'amount': price,
            'products': products
        }
        serializer = PaymentSerializerForOrder(data=payment_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_serializer_class(self, **kwargs):
        return PaymentSerializer

    def post(self, request, *args, **kwargs):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        try:
            payment = Payment.objects.get(
                razorpay_order_id=validated_data['razorpay_order_id']
                )
        except Payment.DoesNotExist:
            raise NotFound('Payment not found.')

        if payment.user != request.user:
            raise ValidationError('Order ID does not match to you.')

        payment.razorpay_payment_id = validated_data['razorpay_payment_id']
        payment.razorpay_signature = validated_data['razorpay_signature']

        try:
            client.utility.verify_payment_signature(validated_data)
        except razorpay.errors.SignatureVerificationError:
            raise ValidationError('Invalid payment signature.')

        payment.paid = True
        payment.save()

        # Update user permissions with the products
        user = request.user
        products_updated = False

        for product in payment.products:
            if product == 'seminar' and not user.is_seminar:
                user.is_seminar = True
                products_updated = True
            elif product == 'sector_assessment' and not user.is_subscriber:
                user.is_subscriber = True
                products_updated = True

        if products_updated:
            user.save()
        return Response({'status': 'Payment verified successfully'},
                        status=status.HTTP_200_OK)
