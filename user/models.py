from django.db import models
import uuid
from django.contrib.auth.models import User
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username,role, phone_number=None, password=None):
        if not email:
            raise ValueError("Users must have an email")
        if not username:
            raise ValueError("Users must have a username")
        if not phone_number:
            raise ValueError("Users must have phone number")
        if not role:
            raise ValueError("Users must have a role")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number,
            role=role,
            # shop = shop
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username,role='Admin', phone_number=None, password = None):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            phone_number = phone_number,
            password=password,
        )
        user.save(using=self._db)
        return user
    



class ShopUser(AbstractBaseUser):
    username = models.CharField(max_length=50)
    email = models.EmailField(verbose_name='email', max_length=60, unique=True)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True,
    )
    # shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    # user_role = models.ForeignKey('UserRole', on_delete=models.CASCADE, null=True)
    date_joined = models.DateField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateField(verbose_name='last login', auto_now=True)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_role']

    objects = MyAccountManager()

    def __str__(self):
        return f"{self.email} ({self.username} - {self.user_role.name})"

    def has_perm(self, perm, obj=None):
        return self.user_role.role.name in ['Admin', 'SuperAdmin']

    def has_module_perms(self, app_label):
        return True
    
    class Meta:
        db_table = 'ShopUser'
    

class Permission(models.Model):
    name = models.CharField(max_length=50)
    # shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

    def __str__(self):
        return self.name[0:50]
    class Meta:
        db_table = 'Permission'


class Role(models.Model):
    name = models.CharField(max_length=50)
    permissions = models.ManyToManyField(Permission)

    def __str__(self):
        return self.name[0:50]
    
    class Meta:
        db_table = 'Role'

# class UserRole(models.Model):
#     id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
#     role = models.OneToOneField(Role, on_delete=models.CASCADE, null= True)
#     name = models.CharField(max_length=60)
#     mobile_no = models.CharField(max_length=10)
#     cdate = models.DateTimeField(auto_now_add=True)
#     udate = models.DateTimeField(auto_now_add=True)


#     def __str__(self):
#         return self.name[0:50]
    
