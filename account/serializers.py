from rest_framework import serializers
from django.contrib.auth.models import User
from. models import Permission, User, Account

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'



class AccountSerealizer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'