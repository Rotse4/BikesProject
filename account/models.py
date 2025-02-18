from django.db import models
import uuid
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# from shop.models import Shop

# from shop.models import Shop

# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None):
        if not username:
            raise ValueError("Users must have a username")
        if not phone_number:
            raise ValueError("Users must have phone number")
        # if not role:
        #     raise ValueError("Users must have a role")

        user = self.model(
            username=username,
            phone_number=phone_number,
            # role=role,
            # shop = shop
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password):
        user = self.create_user(
            username=username,
            phone_number=phone_number,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Account(AbstractBaseUser):
    username = models.CharField(max_length=50, unique=True)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )
    date_joined = models.DateField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateField(verbose_name="last login", auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Add this field
    is_superuser = models.BooleanField(default=False)  # Add this field

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phone_number"]

    objects = MyAccountManager()

    def __str__(self):
        return f"{self.username}"

    def has_perm(self, perm, obj=None):
        return self.is_staff

    def has_module_perms(self, app_label):
        return True

    class Meta:
        db_table = "Account"


class Permission(models.Model):
    name = models.CharField(max_length=50)
    # shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name[0:50]

    class Meta:
        db_table = "Permission"


permisions = ["can_edit", "can_delete", "can_view"]


