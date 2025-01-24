from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver
from django.core.files.base import ContentFile
import requests
import os
import uuid

from shop.models import Shop

# from cart.models import OrderItem

# Create your models here.


import os
import uuid
import requests
from django.core.files.base import ContentFile
from django.db import models


def upload_location(instance, filename):
    # Extract file extension
    extension = os.path.splitext(filename)[-1]
    # Generate a unique filename
    unique_filename = f"{uuid.uuid4().hex[:8]}{extension}"
    # Construct the file path
    file_path = f"images/{instance.shop.id}/{unique_filename}"
    return file_path


CATEGORY_CHOICES = (
    ("featured", "Featured"),
    ("popular", "Popular"),
    ("recommended", "Recommended"),
    ("favorite", "Favorite"),
)


class Item(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=True, default="")
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(default=40)
    # image = models.ImageField(upload_to=upload_location, null=True, blank=True)
    # image_url = models.URLField(max_length=500, null=True, blank=True)
    image1 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image1_url = models.URLField(max_length=500, null=True, blank=True)
    image2 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image2_url = models.URLField(max_length=500, null=True, blank=True)
    image3 = models.ImageField(upload_to=upload_location, null=True, blank=True)
    image3_url = models.URLField(max_length=500, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    stars = models.IntegerField(default=4)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="popular"
    )

    def __str__(self):
        return self.title[:50]

    class Meta:
        ordering = ["-updated", "-created", "id"]

    def save(self, *args, **kwargs):
        def download_image_from_url(image_field, image_url_field):
            """
            Download an image from the URL and save it to the specified image field.
            """
            image_url = getattr(self, image_url_field)
            if image_url and not getattr(self, image_field):
                try:
                    # Fetch the image
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()  # Raise an error for failed requests
                    
                    # Ensure the content is an image
                    if "image" in response.headers.get("Content-Type", ""):
                        extension = os.path.splitext(image_url)[-1] or ".jpg"
                        file_name = f"{uuid.uuid4().hex[:8]}{extension}"
                        setattr(
                            self, image_field, ContentFile(response.content, file_name)
                        )
                    else:
                        raise ValueError(f"Invalid image URL: {image_url}")
                except Exception as e:
                    print(f"Error downloading image from {image_url}: {e}")

        # Populate image fields from URLs
        # download_image_from_url("image", "image_url")
        download_image_from_url("image1", "image1_url")
        download_image_from_url("image2", "image2_url")
        download_image_from_url("image3", "image3_url")

        super().save(*args, **kwargs)
