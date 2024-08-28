from django.contrib import admin

# Register your models here.

from . models import Shop

class ShopAdmin(admin.ModelAdmin):
    model = Shop
    list_display = ("id","name", "cdate", "udate")


admin.site.register(Shop, ShopAdmin)