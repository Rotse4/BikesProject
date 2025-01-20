# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from account.models import Permission
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

# from account.permissions import has_perms
from .models import Roles, Shop
from .serializers import RoleSerializer, ShopSerializer
from rest_framework.decorators import api_view, APIView
from account.permissions import has_perms
from drf_spectacular.utils import extend_schema
from django.utils.decorators import method_decorator


# Create your views here.


@api_view(["GET"])
def shop_list(request):

    if request.method == "GET":
        shops = Shop.objects.all()
        serializer = ShopSerializer(shops, many=True)
        return Response({"shops": serializer.data})


class RoleCreateAPIView(APIView):
    @extend_schema(
        operation_id="create_role",
        summary="Create a new role",
        description="Create a new role with a name, permissions, and associated shop.",
         request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Manager"},
                    "permissions": {
                        "type": "array",
                        "items": {"type": "String"},
                        "example": ["can_view", "can_delete", "can_add","can_edit"],
                    },
                },
                "required": ["name"],
            }
        },
         
         responses={
            200: OpenApiResponse(
                # response=RoleSerializer,
                description="Role created successfully."
            ),
            400: OpenApiResponse(
                description="Validation errors.",
                examples={
                    "application/json": {
                        "name": ["This field is required."],
                        "permissions": ["Invalid permission ID."],
                    }
                },
            ),
        },
    )
    @method_decorator(has_perms(["can_add"]))
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["shop"] = request.shop_id
        serializer = RoleSerializer(data=data)
        if serializer.is_valid():
            # Check if shop exists and is valid
            shop_id = request.data.get('shop')
            shop = get_object_or_404(Shop, id=shop_id)

            # Save the role
            role = serializer.save(shop=shop)

            # Handle permissions (if needed, e.g., by ID list)
            permission_ids = request.data.get('permissions', [])
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)

            return Response(RoleSerializer(role).data, status=200)
        return Response(serializer.errors, status=400)
    
    

class AssignRoleAPIView(APIView):
    @extend_schema(
        operation_id="assign_role",
        summary="Assign a role to a user",
        description="Assign an existing role to a user in the shop the user is logged into.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "example": 123},
                    "role_id": {"type": "integer", "example": 1},
                },
                "required": ["user_id", "role_id"],
            }
        },
        responses={
            200: OpenApiResponse(
                description="Role assigned successfully."
            ),
            400: OpenApiResponse(
                description="Validation errors.",
                examples={
                    "application/json": {
                        "user_id": ["This field is required."],
                        "role_id": ["Invalid role ID."],
                    }
                },
            ),
        },
    )
    @method_decorator(has_perms(["can_update"]))
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")

        # Get the shop associated with the logged-in user
        shop = request.shop  # Assumed that the user's shop is stored in the request object

        # Validate role existence in the shop
        role = get_object_or_404(Roles, id=role_id, shop=shop)

        # Assign role to user
        user = get_object_or_404(Roles, id=user_id)
        user.role = role
        user.save()

        return Response(
            {"message": "Role assigned successfully."},
            status=200,
        )