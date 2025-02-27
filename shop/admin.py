from django.contrib import admin

# Register your models here.

from . models import  OrderDuration, Roles, Shop,ShopUSer

class ShopAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ("id","name", "cdate", "udate")


admin.site.register(Shop, ShopAdmin)

class RoleAdmin(admin.ModelAdmin):
    model = Roles
    list_display = ("id","name", "shop")
    
admin.site.register(Roles, RoleAdmin)


# class ShopRoleAdmin(admin.ModelAdmin):
#     model = ShopRole
#     list_display = ("id","shop_role", "shop", "name")


# admin.site.register(ShopRole, ShopRoleAdmin)

# class UserShopRoleAdmin(admin.ModelAdmin):
#     model = UserShopRole
#     list_display = ("id","user", "shop_role", "name")


# admin.site.register(UserShopRole, UserShopRoleAdmin)

class ShopeUserAdmin(admin.ModelAdmin):
    model = ShopUSer
    list_display = ("id","shop", "user", "role")


admin.site.register(ShopUSer, ShopeUserAdmin)

class OrderDurationAdmin(admin.ModelAdmin):
    model = OrderDuration
    list_display = ("id","time", "price")


admin.site.register(OrderDuration, OrderDurationAdmin)



    
                     

