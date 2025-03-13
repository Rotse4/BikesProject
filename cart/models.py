from django.db import models

from account.models import Account
from item.models import Item
from django.utils.timezone import now


# Create your models here.
    

# class Order(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE)
#     payment = models.ForeignKey("Payment", on_delete=models.CASCADE, null=True)
#     # pickup = models.BooleanField(null=True)
#     # region = models.TextField(max_length=100, null=True)
#     # exactLocation = models.TextField(
#     #     null=True,
#     # )
#     order_date = models.DateTimeField(auto_now_add=True)
#     total = models.DecimalField(decimal_places=5, max_digits=10, default=0)
#     payment_number = models.CharField(max_length=12)
#     confirmed = models.BooleanField(default=False)
#     start_time = models.DateTimeField(null=True, blank=True, default=now)
#     end_time = models.DateTimeField(null=True, blank=True, default=now)

#     def __str__(self):
#         return str(self.id)


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, null=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null = True, blank=True)
    payment = models.ForeignKey("Payment", on_delete=models.CASCADE, null=True)
    # order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    # quantity = models.PositiveIntegerField(default=0)
    # date_added = models.DateTimeField(auto_now_add=True)
    # rating = models.IntegerField(
    #     null=True,
    # )
    price = models.DecimalField(decimal_places=5, max_digits=10, default=40)
    start_time = models.DateTimeField(null=True, blank=True, default=now)
    end_time = models.DateTimeField(null=True, blank=True)
    active = models.BooleanField(null=True, blank=True)
    confirmed = models.BooleanField(default=False, blank=True, null=True)
    # sub_total = models.DecimalField(decimal_places=5, max_digits=10, default=0)

    def __str__(self):
        return str(self.item)

    # def save(self, *args, **kwargs):
    #     self.sub_total = self.quantity * self.price
    #     super().save(*args, **kwargs)

    # def set_rating(self, rate):
    #     if self.order.confirmed:
    #         self.rating = rate
    #         self.save()

    # def total(self):
    #     self.sub_total = self.quantity * self.price

    #     return self.sub_total


class Payment(models.Model):
    phone_no = models.CharField(max_length=10)
    mpesa_transaction_id = models.CharField(max_length=70, default=0)

    def __str__(self):
        return str(self.id)
