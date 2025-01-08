from rest_framework.decorators import api_view, APIView

from account.models import Account

# from account.permissions import has_perms
from shop.models import Roles, ShopUSer
from .serializers import AccountSerealizer, SelectShopSerializer

# from .auth_middware import TokenAuthenticationMiddleware
from drf_spectacular.utils import extend_schema
import datetime
from rest_framework.response import Response
import jwt
from django.contrib.auth import authenticate
from rest_framework import serializers

# from drf_spectacular.views import


class TokenBuilder:
    def __init__(self) -> None:
        self.secret = "my_secret_key"

    @staticmethod
    def accessToken(payload={}, time=3):
        tokenBuilder = TokenBuilder()

        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=time)
        access_token = jwt.encode(payload, tokenBuilder.secret, algorithm="HS256")
        return access_token

    def refreshToken(payload={}, time=30):
        tokenBuilder = TokenBuilder()

        payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(days=time)
        access_token = jwt.encode(payload, tokenBuilder.secret, algorithm="HS256")
        return access_token


@extend_schema(
    request=AccountSerealizer,
    responses={
        200: {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "example": "+123456789",
                                },
                                "username": {"type": "string", "example": "john_doe"},
                                "id": {"type": "integer", "example": 1},
                            },
                        },
                        "token": {
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                                "refresh_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                            },
                        },
                    },
                },
            },
        },
        400: {
            "type": "object",
            "properties": {"error": {"type": "string", "example": "Invalid input"}},
        },
    },
    summary="User Registration",
    description="Register a new user with username, phone number, and password.",
    tags=["Authentication"],
)
@api_view(["POST"])
def registration_view(request):
    serializer = AccountSerealizer(data=request.data)
    data = {}
    if serializer.is_valid():
        account = serializer.save()
        # data['response']= "succsssfully registered a new user."
        data["phone_number"] = account.phone_number
        data["username"] = account.username
        data["id"] = account.pk
        # data['shop_id']=account.shop

        access_token = TokenBuilder.accessToken(payload=data)

        refresh_token = TokenBuilder.refreshToken(payload=data)

        secret_key = "your_secret_key"

        return Response(
            {
                "payload": {
                    "user": data,
                    "token": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    },
                }
            }
        )
    else:
        data = serializer.errors

    return Response(data, status=400)


# @extend_schema()
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "example": "john_doe"},
                "password": {"type": "string", "example": "password123"},
                "shop_name": {"type": "string", "example": "Shop A", "nullable": True},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "example": "+123456789",
                                },
                                "username": {"type": "string", "example": "john_doe"},
                                "id": {"type": "integer", "example": 1},
                                "shop_name": {
                                    "type": "string",
                                    "example": "Shop A",
                                    "nullable": True,
                                },
                            },
                        },
                        "token": {
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                                "refresh_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                            },
                        },
                    },
                }
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid credentials"}
            },
        },
    },
    summary="User Login",
    description="Authenticate a user using username, password, and optionally a shop name.",
    tags=["Authentication"],
)
@api_view(["POST"])
def adminLogin(request):
    username = request.data.get("username")
    print(username)
    password = request.data.get("password")
    print(f"pass {password}")
    selected_shop_name = request.data.get(
        "shop_name"
    )  # Expecting the selected shop name if multiple shops exist
    print(f"selected shop name: {selected_shop_name}")

    account = authenticate(request, username=username, password=password)

    if account is not None:
        shop_users = ShopUSer.objects.filter(user=account)

        if shop_users.count() > 1 and selected_shop_name is None:
            # If multiple shops exist, return them to the user for selection
            shops = [
                {"name": shop.shop.name, "id": shop.shop.id} for shop in shop_users
            ]
            return Response(
                {
                    "error": "Multiple shops found.",
                    "shops": shops,
                    "message": "Please select a shop to log in.",
                },
                status=200,
            )

        elif shop_users.count() == 1:
            # If only one shop exists, proceed with login
            shop_user = shop_users.first()
            return _generate_token_response(account, shop_user.shop)

        elif shop_users.count() == 0:
            return _generate_token_response(account, None)

        # Handle case where user has multiple shops and selects one by name
        if selected_shop_name:
            try:
                selected_shop_user = shop_users.get(shop__name=selected_shop_name)
                return _generate_token_response(account, selected_shop_user.shop)
            except ShopUSer.DoesNotExist:
                return Response({"error": "Invalid shop selection"}, status=400)

    # Authentication failed
    return Response({"error": "Invalid credentials"}, status=400)


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "example": "john_doe"},
                "password": {"type": "string", "example": "password123"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "example": "+123456789",
                                },
                                "username": {"type": "string", "example": "john_doe"},
                                "id": {"type": "integer", "example": 1},
                                "shop_name": {
                                    "type": "string",
                                    "example": "Shop A",
                                    "nullable": True,
                                },
                            },
                        },
                        "token": {
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                                "refresh_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                            },
                        },
                    },
                }
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid credentials"}
            },
        },
    },
    summary="User Login",
    description="Authenticate a user using username and password. Shop name is not required for normal users.",
    tags=["Authentication"],
)
@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "example": "john_doe"},
                "password": {"type": "string", "example": "password123"},
            },
            "required": ["username", "password"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "payload": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "phone_number": {
                                    "type": "string",
                                    "example": "+123456789",
                                },
                                "username": {"type": "string", "example": "john_doe"},
                                "id": {"type": "integer", "example": 1},
                                "shop_name": {
                                    "type": "string",
                                    "example": "Shop A",
                                    "nullable": True,
                                },
                            },
                        },
                        "token": {
                            "type": "object",
                            "properties": {
                                "access_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                                "refresh_token": {
                                    "type": "string",
                                    "example": "eyJhb...",
                                },
                            },
                        },
                    },
                }
            },
        },
        400: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Invalid credentials"}
            },
        },
    },
    summary="User Login",
    description="Authenticate a user using username and password. Users with shops will be automatically directed to the first shop.",
    tags=["Authentication"],
)
@api_view(["POST"])
def userLogin(request):
    username = request.data.get("username")
    password = request.data.get("password")

    # Authenticate the user
    account = authenticate(request, username=username, password=password)

    if account is not None:
        # Fetch associated shops for the user
        shop_users = ShopUSer.objects.filter(user=account)

        if shop_users.exists():
            # Automatically direct the user to the first shop
            first_shop_user = shop_users.first()
            return _generate_token_response(account, first_shop_user.shop)
        else:
            # No associated shops, proceed as a normal user
            return _generate_token_response(account, None)

    # Authentication failed
    return Response({"error": "Invalid credentials"}, status=400)


def _generate_token_response(user, shop):
    """
    Helper function to generate a token response for the user.
    """
    # Assuming you have logic to generate access and refresh tokens
    access_token = "generated_access_token"  # Replace with actual token generation
    refresh_token = "generated_refresh_token"  # Replace with actual token generation

    return Response(
        {
            "payload": {
                "user": {
                    "phone_number": getattr(user, "phone_number", None),
                    "username": user.username,
                    "id": user.id,
                    "shop_name": shop.name if shop else None,
                },
                "token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            }
        },
        status=200,
    )

def _generate_token_response(account, shop):
    if shop == None:
        data = {
            "phone_number": account.phone_number,
            "username": account.username,
            "id": account.pk,
        }
    else:
        data = {
            "phone_number": account.phone_number,
            "username": account.username,
            "id": account.pk,
            "shop_id": str(shop.id),  # Send the selected shop ID
        }

    access_token = TokenBuilder.accessToken(payload=data)
    refresh_token = TokenBuilder.refreshToken(payload=data)

    return Response(
        {
            "payload": {
                "user": data,
                "token": {"access_token": access_token, "refresh_token": refresh_token},
            }
        }
    )


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "shop_id": {
                    "type": "string",
                    "example": "acde070d-8c4c-4f0d-9d8a-162843c10333",
                },
            },
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "example": "Logged in successfully to the selected shop.",
                },
                "shop_id": {"type": "integer", "example": 1},
                "shop_name": {"type": "string", "example": "Super Bikes"},
            },
        },
        404: {
            "type": "object",
            "properties": {
                "error": {"type": "string", "example": "Shop not found for this user."}
            },
        },
    },
    summary="Select Shop",
    description="Allows an authenticated user to select and log into a specific shop.",
    tags=["Shop"],
)
@api_view(["POST"])
def select_shop(request):
    shop_id = request.data.get("shop_id")
    account = request.user  # Ensure you get the authenticated user

    try:
        shop_user = ShopUSer.objects.get(user=account, shop__id=shop_id)
        # Proceed with any additional logic needed, such as setting session data, etc.

        data = {
            "message": "Logged in successfully to the selected shop.",
            "shop_id": shop_user.shop.id,
            "shop_name": shop_user.shop.name,
        }

        return Response(data)
    except ShopUSer.DoesNotExist:
        return Response({"error": "Shop not found for this user."}, status=404)


# @extend_schema
@api_view(["GET"])
# @has_perms('can_edit')
def viewUsers(request):
    if request.account.is_authenticated:
        print(f"Authenticated user: {request.account.username}")
    else:
        print("User is not authenticated")

    users = Account.objects.all()
    serializer = AccountSerealizer(users, many=True)
    return Response({"users": serializer.data})


class ShopList(APIView):
    def get(self, request, format=None):

        roles = Roles.objects.all()
        roles_data = [{"id": role.id, "name": role.name} for role in roles]
        
        print("request.account")
        return Response(roles_data, status=200)
