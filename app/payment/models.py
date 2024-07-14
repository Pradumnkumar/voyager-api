from django.db import models
from core.models import User


# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True,
                                           null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True,
                                          null=True)
    amount = models.FloatField()
    products = models.JSONField(blank=True, default=list)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    no_of_times_allowed = models.IntegerField()
    discount = models.IntegerField()
