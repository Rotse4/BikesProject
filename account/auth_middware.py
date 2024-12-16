from django.http import JsonResponse
import jwt
from django.urls import reverse
from django.contrib import admin
from django.urls import resolve

from shop.models import ShopUSer
from . models import Account

SECRET_KEY = 'my_secret_key'

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        excluded_routes = [
            '/user/register', '/user/login', '/user/', '/favicon.ico',
            '/cart/callback', '/account/refresh', '/schema',
        ]

        if (request.path in excluded_routes or
            request.path.startswith('/admin/') or
            request.path.startswith('/static/') or
            request.path.startswith('/media/images/') or
            request.path.startswith('/api/')):
            return self.get_response(request)

        # Get the access token from the request header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'message': 'Invalid access token'}, status=401)

        token = auth_header.split("Bearer ")[1]

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token['id']
            user = Account.objects.get(id=user_id)

            request.account = user

        except jwt.ExpiredSignatureError:
            return JsonResponse({'message': 'Access token has expired'}, status=401)
        except (jwt.InvalidTokenError, Account.DoesNotExist):
            return JsonResponse({'message': 'Invalid access token'}, status=401)

        return self.get_response(request)