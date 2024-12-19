from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
# Register your models here.

from . models import Permission,Account

class AccountAdmin(UserAdmin):
    model = Account
    list_display = ("id","username","phone_number","date_joined")
    fieldsets = ()
    list_filter = (['id'])
    filter_horizontal =()

class PermissionAdmin(admin.ModelAdmin):
    model = Permission
    list_display = ("id","name")



admin.site.register(Account, AccountAdmin)

admin.site.register(Permission, PermissionAdmin)

# admin.site.register(Role, RoleAdmin)


# class ShopUser(AbstractBaseUser):
#     username = models.CharField(max_length=50, unique=True)
#     # email = models.EmailField(verbose_name='email', max_length=60, unique=True)
#     phone_number = models.CharField(
#         max_length=15,
#         unique=True,
#         null=True,
#         blank=True,
#     )
#     # shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
#     # user_role = models.ForeignKey('UserRole', on_delete=models.CASCADE, null=True)
#     date_joined = models.DateField(verbose_name='date joined', auto_now_add=True)
#     last_login = models.DateField(verbose_name='last login', auto_now=True)
#     is_active = models.BooleanField(default=True)

#     USERNAME_FIELD = 'username'
#     REQUIRED_FIELDS = ['user_role']

#     objects = MyAccountManager()

#     def __str__(self):
#         return f"({self.username} - {self.user_role.name})"

#     def has_perm(self, perm, obj=None):
#         return self.user_role.role.name in ['Admin', 'SuperAdmin']

#     def has_module_perms(self, app_label):
#         return True
    
#     class Meta:
#         db_table = 'ShopUser'
    

# class Permission(models.Model):
#     name = models.CharField(max_length=50)
#     # shop = models.ForeignKey(Shop, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name[0:50]
#     class Meta:
#         db_table = 'Permission'


# class Role(models.Model):
#     name = models.CharField(max_length=50)
#     permissions = models.ManyToManyField(Permission)

#     def __str__(self):
#         return self.name[0:50]
    
#     class Meta:
#         db_table = 'Role'