# from django.shortcuts import render
from rest_framework.response import Response

from account.permissions import has_perms
from . models import Shop
from . serializers import ShopSerializer
from rest_framework.decorators import api_view

# Create your views here.

@api_view(["GET"])
@has_perms('can_edit')
def shop_list(request):
    
    if request.method == "GET":
        shops = Shop.objects.all()
        serializer = ShopSerializer(shops, many = True)
        return Response({"shops":serializer.data})