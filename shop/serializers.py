from rest_framework import serializers

from account.models import Permission
from .models import Roles, Shop, ShopUSer

class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name', 'owner', 'cdate', 'udate']
        
class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Permission.objects.all(),
    )

    class Meta:
        model = Roles
        fields = ['id', 'name', 'permissions', 'shop']
        read_only_fields = ['shop']  # Shop is set by the view, not the request
        
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']
        

class ShopUserSerializer(serializers.ModelSerializer):
    # Add a custom field to fetch the user's name
    user = serializers.CharField(source="user.username")  # Assumes `user` is a ForeignKey to `Account`
    role = serializers.CharField(source="role.name")
    shop = serializers.CharField(source="shop.name")

    class Meta:
        model = ShopUSer
        fields = '__all__'