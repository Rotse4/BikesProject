from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem, Payment
from django.forms import TextInput
from django.db import models

class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = ('id', 'account', 'total', 'payment', 'order_date', 'payment_number', 'pickup', 'region', 'exactLocation', 'confirmed')


class OderItemAdmin(admin.ModelAdmin):
    model = OrderItem
    list_display = ( 'item', 'order','quantity', 'date_added','rating' ,'price', 'sub_total')


class PaymentAdmin(admin.ModelAdmin):
    model = Payment
    list_display = ('id','phone_no', 'mpesa_transaction_id')

admin.site.register(Order, OrderAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(OrderItem, OderItemAdmin)