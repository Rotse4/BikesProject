# from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.response import Response

from account.models import Permission

# from account.permissions import has_perms
from .models import Shop
from .serializers import RoleSerializer, ShopSerializer
from rest_framework.decorators import api_view, APIView
from account.permissions import has_perms
from drf_spectacular.utils import extend_schema


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
        request=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: "Validation errors",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = RoleSerializer(data=request.data)
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