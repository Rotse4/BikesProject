from django.contrib import admin
from django.utils.html import format_html
from django.utils.text import Truncator
from .models import Item


class ItemAdmin(admin.ModelAdmin):
    model = Item
    search_fields = ["title", "description"]  # Allow searching by title and description
    list_display = (
        "id",
        "shop",
        "title",
        "category",
        "stars",
        "price",
        "get_images",
        "short_description",
        "created",
        "updated",
    )
    list_filter = [
        "category",
        "stars",
        "created",
        "updated",
    ]  # Add filters for easier navigation
    ordering = ["-updated", "-created"]  # Order by most recently updated/created

    def get_images(self, obj):
        """
        Display thumbnails for the item's images, with fallback for missing images.
        """
        # Use default placeholder for missing images
        image1_url = (
            obj.image1.url if obj.image1 else "/static/images/default-image.jpg"
        )
        image2_url = (
            obj.image2.url if obj.image2 else "/static/images/default-image.jpg"
        )
        image3_url = (
            obj.image3.url if obj.image3 else "/static/images/default-image.jpg"
        )

        return format_html(
            '<img src="{}" width="50" height="50" /> '
            '<img src="{}" width="50" height="50" /> '
            '<img src="{}" width="50" height="50" />',
            image1_url,
            image2_url,
            image3_url,
        )

    # get_images.short_description = 'Images'

    get_images.short_description = "Images"

    def short_description(self, obj):
        max_length = 50  # Maximum length of the truncated description
        return Truncator(obj.description).chars(max_length)

    short_description.short_description = "Description"

    def has_add_permission(self, request):
        # Allow only superusers or staff to add items
        return request.user.is_superuser or request.user.is_staff


# Register the model with the customized admin
admin.site.register(Item, ItemAdmin)
