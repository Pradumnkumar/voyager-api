from django.contrib import admin
from .models import Payment
# Register your models here.


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'id', 'amount']
    readonly_fields = ('user', 'products', 'razorpay_order_id',
                       'razorpay_payment_id',
                       'razorpay_signature', 'amount',
                       'paid', 'created_at')
