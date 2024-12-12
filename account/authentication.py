import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from account.models import Account
from shop.models import ShopUSer

SECRET_KEY = 'my_secret_key'

class CustomJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None  # Allow unauthenticated access if not required

        token = auth_header.split("Bearer ")[1]
        try:
            # Decode token
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = decoded_token.get('id')
            shop_id = decoded_token.get('shop_id')

            # Fetch user
            user = Account.objects.get(id=user_id)

            # Attach shop information if available
            if shop_id:
                user_shop = ShopUSer.objects.get(shop=shop_id, user=user)
                request.shop_id = shop_id
                request.shop_user = user_shop.id

            # Attach user to request
            return user, token

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Access token has expired")
        except (jwt.InvalidTokenError, Account.DoesNotExist):
            raise AuthenticationFailed("Invalid access token")

        return None


from drf_spectacular.extensions import OpenApiAuthenticationExtension

class CustomJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'account.authentication.CustomJWTAuthentication'  # Full path to your class
    name = 'CustomJWT'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'Enter your JWT token in the format: Bearer <token>',
        }
