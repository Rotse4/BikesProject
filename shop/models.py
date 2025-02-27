from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

from account.models import Account, Permission


# # Create your models here.


class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    cdate = models.DateTimeField(auto_now_add=True)
    udate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name[0:50]

    class Meta:
        db_table = "Shop"


# class ShopRole(models.Model):
#     name = models.CharField(max_length=255, blank=True)
#     shop_role = models.ForeignKey(Role, on_delete=models.CASCADE)
#     shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

#     # permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

#     def save(self, *args, **kwargs):
#         # Combine shop_role and shop to create the name
#         self.name = f"{self.shop_role.name} - {self.shop.name}"
#         super(ShopRole, self).save(*args, **kwargs)

#     def __str__(self):
#         return self.name

#     class Meta:
#         db_table = "ShopeRole"


# class UserShopRole(models.Model):
#     user = models.ForeignKey(Account, on_delete=models.CASCADE)
#     shop_role = models.ForeignKey(ShopRole, on_delete=models.CASCADE)
#     name = models.CharField(max_length=255, blank=True)

#     def save(self, *args, **kwargs):
#         # Combine shop_role and shop to create the name
#         self.name = f"{self.shop_role.name} - {self.user.username}"
#         super(UserShopRole, self).save(*args, **kwargs)

#     def __str__(self):shop
#         return self.name
#     class Meta:
#         db_table = 'UserShopRole'


class Roles(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name[0:50]

    class Meta:
        db_table = "Role"
        unique_together = ("name", "shop")  #


class ShopUSer(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    role = models.ForeignKey(Roles, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Combine shop_role and shop to create the name
        self.name = f"{self.shop.name} - {self.role.name}"
        super(ShopUSer, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "ShopUser"
        unique_together = ("name", "shop")


class OrderDuration(models.Model):
    time = models.CharField(max_length=100, unique=True)
    price = models.CharField(max_length=100)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
