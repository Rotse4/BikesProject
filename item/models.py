from django.db import models
from django.db.models.signals import post_delete,pre_save
from django.utils.text import slugify
from django.conf import settings
from django.dispatch import receiver

from shop.models import Shop
# from cart.models import OrderItem

# Create your models here.


def upload_location(instance, filename):
    file_path = 'images/{shop_id}/{title}-{filename}'.format(
        shop_id=str(instance.shop.id),
        title=str(instance.title),
        filename=filename

    )
    return file_path

CATEGORY_CHOICES = (
        ('featured', 'Featured'),
        ('popular', 'Popular'),
        ('recommended', 'Recommended'),
        ('favorate', 'Favorate'),

    )

class Item(models.Model):
    # owner= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    shop= models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=True, default='')
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField(default=40)
    image = models.ImageField(upload_to=upload_location, null=False, blank=False)
    image1 = models.ImageField(upload_to=upload_location, null=False, blank=False, default='path/to/default/image.jpg')
    image2 = models.ImageField(upload_to=upload_location, null=False, blank=False,default='path/to/default/image.jpg')
    image3 = models.ImageField(upload_to=upload_location, null=False, blank=False,default='path/to/default/image.jpg')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    stars = models.IntegerField(default=4)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='popular')
    # slug =models.SlugField(blank=True, unique=True)
    

    def __str__(self):
        return self.title[0:50]

    class Meta:
        ordering = ['updated','created','id']