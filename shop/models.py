from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from user.models import Permission, Role, ShopUser



# class MyAccountManager(BaseUserManager):
#     def create_user(self, phone_number, username, password=None):
#         if not phone_number:
#             raise ValueError("Users must have phone number")
#         if not username:
#             raise ValueError("Users must have a username")

#         user = self.model(
#             # email=self.normalize_email(phone_number),
#             phone_number=phone_number,
#             username=username,
#         )
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, phone_number, username, password):
#         user = self.create_user(
#             # email=self.normalize_email(email),
#             phone_number=phone_number,
#             username=username,
#             password=password,
#         )
#         user.save(using=self._db)
#         return user

# class UsualUser(AbstractBaseUser):
#     id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
#     phone_number = models.CharField(
#         max_length=15,
#         unique=True,
#         null=True,
#         blank=True,
#     )
#     username = models.CharField(max_length=30, unique=True)
#     date_joined = models.DateField(verbose_name='date joined', auto_now_add=True)
#     last_login = models.DateField(verbose_name='last login', auto_now=True)
#     is_active = models.BooleanField(default=True)

#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['phone_number']

#     objects =MyAccountManager()

#     def __str__(self):
#         return self.username
    

#     # def has_perm(self, perm, obj=None):
#     #     return self.is_admin
    
#     def has_module_perms(self, app_lebel):
#         return True
    
    
# # Create your models here.


class Shop(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    cdate = models.DateTimeField(auto_now_add=True)
    udate = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name[0:50]
    class Meta:
        db_table = 'Shop'
    
class ShopRole(models.Model):
    shop_role = models.ForeignKey(Role, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        # Combine shop_role and shop to create the name
        self.name = f"{self.shop_role.name} - {self.shop.name}"
        super(ShopRole, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'ShopeRole'


class UserShopRole(models.Model):
    user = models.ForeignKey(ShopUser, on_delete=models.CASCADE)
    shop_role = models.ForeignKey(ShopRole, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        # Combine shop_role and shop to create the name
        self.name = f"{self.shop_role.name} - {self.shop.name}"
        super(ShopRole, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    class Meta:
        db_table = 'UserShopRole'

    
                     
