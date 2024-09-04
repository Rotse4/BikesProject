from django.contrib import admin

# Register your models here.
from django.utils.html import format_html

from .models import Item
from django.utils.text import Truncator

class ItemAdmin(admin.ModelAdmin):
    model = Item
    search_fields=['title']
    list_display = ('id', 'shop','title', 'category', 'stars', 'price', 'get_image', 'short_description', 'created', 'updated')

    def get_image(self, obj):
        return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
    get_image.short_description = 'Image'

    def short_description(self, obj):
        max_length = 50  # Maximum length of the truncated description
        truncated = Truncator(obj.description).chars(max_length)
        return truncated
    short_description.short_description = 'Description'

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.is_staff:
            return True
        return False

admin.site.register(Item, ItemAdmin)