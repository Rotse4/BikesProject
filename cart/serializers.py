from rest_framework import serializers
from django.contrib.auth.models import User

from account.models import Account
# from rest_framework.serializers import ModelSerializer
from .models import OrderItem, Order



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','account','order_date','payment_number','total','confirmed', 'pickup', 'region', 'exactLocation']

        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

        
class RatingSerializer(serializers.Serializer):
    rating = serializers.IntegerField(min_value=1, max_value=5)



