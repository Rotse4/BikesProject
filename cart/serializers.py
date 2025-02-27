from rest_framework import serializers
from django.contrib.auth.models import User

from account.models import Account
from shop.models import OrderDuration

# from rest_framework.serializers import ModelSerializer
from .models import OrderItem


# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = ["id", "account", "order_date", "payment_number", "total", "confirmed"]


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"


class RatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)


class OrderDurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderDuration
        fields = "__all__"
