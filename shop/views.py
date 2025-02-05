# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from account.models import Account, Permission
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse

# from account.permissions import has_perms
from .models import Roles, Shop, ShopUSer
from .serializers import PermissionSerializer, RoleSerializer, ShopSerializer
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
        summary="Create a new role (requires roles_control_permissions)",
        description="Create a role by name with permissions identified by their names.",
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "example": "Manager"},
                    "permissions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "example": ["view_shop", "edit_shop"],
                    },
                },
                "required": ["name"],
            }
        },
        responses={
            200: OpenApiResponse(description="Role created successfully."),
            400: OpenApiResponse(
                description="Validation errors.",
                examples={
                    "application/json": {
                        "name": ["This field is required."],
                        "permissions": ["Invalid permission name."],
                    }
                },
            ),
        },
    )
    @method_decorator(has_perms(["roles_control_permissions"]))
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        data["shop"] = request.shop_id  # Set shop from request context
        serializer = RoleSerializer(data=data)

        if serializer.is_valid():
            shop = get_object_or_404(Shop, id=request.shop_id)
            role = serializer.save(shop=shop)  # Serializer handles permissions
            return Response(RoleSerializer(role).data, status=200)
        return Response(serializer.errors, status=400)


class AssignRoleAPIView(APIView):
    @extend_schema(
        operation_id="assign_role",
        summary="Assign a role to a user requires[roles_control_permissions]",
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
            200: OpenApiResponse(description="Role assigned successfully."),
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
    @method_decorator(has_perms(["roles_control_permissions"]))
    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        role_id = request.data.get("role_id")

        if not user_id or not role_id:
            return Response(
                {"error": "Both user_id and role_id are required."},
                status=400,
            )

        # Get the shop associated with the logged-in user
        shop = (
            request.shop_id
        )  # Assuming the user's shop is stored in the request object

        # Validate that the role exists in the shop
        role = get_object_or_404(Roles, id=role_id, shop=shop)

        # Validate that the user exists
        user = get_object_or_404(Account, id=user_id)

        # Create or update ShopUser
        shop_user, created = ShopUSer.objects.update_or_create(
            shop=Shop.objects.get(id=shop),
            user=user,
            defaults={"role": role},
        )

        return Response(
            {"message": "Role assigned successfully.", "created": created},
            status=200,
        )


@extend_schema(
    operation_id="view Permissions",
    summary="View Permissions requires[roles_control_permissions]",
    tags=["roles"],
    # description="Create a new role with a name, permissions, and associated shop.",
)
class PermissionListAPIView(APIView):
    # permission_classes = [IsAuthenticated]  # Only allow authenticated users

    def get(self, request, *args, **kwargs):
        permissions = Permission.objects.all()  # Fetch all permissions
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=200)
