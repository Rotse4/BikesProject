from rest_framework.decorators import api_view

from account.models import Account
from account.permissions import has_perms
from . serializers import AccountSerealizer
# from .auth_middware import TokenAuthenticationMiddleware
import datetime
from rest_framework.response import Response
import jwt
from django.contrib.auth import authenticate

class TokenBuilder:
    def __init__(self) -> None:
        self.secret="my_secret_key"
    @staticmethod
    def accessToken(payload={},time=3):
         tokenBuilder = TokenBuilder()

                
         payload['exp']=datetime.datetime.utcnow() + datetime.timedelta(days=time)
         access_token = jwt.encode(payload, tokenBuilder.secret, algorithm='HS256')
         return access_token
    def refreshToken(payload={},time=30):
         tokenBuilder = TokenBuilder()

                
         payload['exp']=datetime.datetime.utcnow() + datetime.timedelta(days=time)
         access_token = jwt.encode(payload, tokenBuilder.secret, algorithm='HS256')
         return access_token


@api_view(['POST'])
def registration_view(request):
    serializer  = AccountSerealizer(data=request.data)
    data={}
    if serializer.is_valid():
        account = serializer.save()
        # data['response']= "succsssfully registered a new user."
        data['phone_number'] = account.phone_number
        data['username'] = account.username
        data['id'] = account.pk

        access_token=TokenBuilder.accessToken(payload=data)

        refresh_token=TokenBuilder.refreshToken(payload=data)

        secret_key = 'your_secret_key'

        return Response({'payload':{'user':data,'token':{'access_token':access_token, 'refresh_token': refresh_token}}})
    else:
        data = serializer.errors
        
    return Response(data, status=400)


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # print(request.data.get('password'))

    account = authenticate(request, username=username, password=password)
    print(f"acoount {account}")
    if account is not None:
        # Authentication successful, generate tokens
        print("here")
        data = {}
        data['phone_number'] = account.phone_number
        data['username'] = account.username
        data['id'] = account.pk

        access_token = TokenBuilder.accessToken(payload=data)
        refresh_token = TokenBuilder.refreshToken(payload=data)

        return Response({
            'payload': {
                'user': data,
                'token': {
                    'access_token': access_token,
                    'refresh_token': refresh_token
                }
            }
        })
    else:
        # Authentication failed
        return Response({'error': 'Invalid credentials'}, status=400)


@api_view(['GET'])
@has_perms('can_add')
def viewUsers(request):
    if request.account.is_authenticated:
        print(f"Authenticated user: {request.account.username}")
    else:
        print("User is not authenticated")

    users = Account.objects.all()
    serializer = AccountSerealizer(users, many=True)
    return Response({"users": serializer.errors})

