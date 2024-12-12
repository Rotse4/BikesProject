from rest_framework import serializers
from django.contrib.auth.models import User

from shop.models import Shop
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

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    
    class Meta:
        model = Account
        fields = ['username','phone_number','password','password2']
        extra_kwargs = {
            'password':{'write_only': True}
        }

    def save(self):
        account = Account(
            username = self.validated_data['username'],
            phone_number = self.validated_data['phone_number'],
        )
        password = self.validated_data['password']
        password2=self.validated_data['password2']

        if password != password2:
            raise serializers.ValidationError({'password': "Passwords dont't match"})
        account.set_password(password)
        account.save()
        return account  
    
class SelectShopSerializer (serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'