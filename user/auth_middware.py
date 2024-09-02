from django.http import JsonResponse
import jwt
from django.urls import reverse
from django.contrib import admin
from django.urls import resolve
from . models import ShopUser

SECRET_KEY = 'my_secret_key'

class TokenAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Exclude specific routes from token authentication if needed
        print(request.path)
        excluded_routes = ['/api/account/register', '/api/account/log', '/api','/favicon.ico','/cart/callback', '/api/account/refresh']

        if request.path in excluded_routes or request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/images/') or request.path.startswith('/api'):
            return self.get_response(request)

        # Get the access token from the request header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'message': 'Invalid access token'}, status=401)

        token = auth_header.split("Bearer ")[1]
        

        try:
            # Verify and decode the access token using the secret key
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

            # Extract user information from the decoded token
            user_id = decoded_token['id']
            print(user_id)
            username = decoded_token['username']

            # Retrieve the Account object based on the user ID
            user = Account.objects.get(id=user_id)
            
            print(user)

            # Assign the user object to the request
            request.account = user
            # setattr(request, '_cached_user', user)

        except jwt.ExpiredSignatureError:
            return JsonResponse({'message': 'Access token has expired'}, status=401)
        except (jwt.InvalidTokenError, Account.DoesNotExist):
            return JsonResponse({'message': 'Invalid access token'}, status=401)

        return self.get_response(request)
