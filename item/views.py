from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from account.permissions import has_perms
from .serializers import ItemSerializer
from .models import Item
from rest_framework import status
from django.db.models import Q
from django.utils.decorators import method_decorator


# @api_view(['POST'])
# # Create your views here.

# @extend_schema(
#     parameters=[{
#         'name': 'shop_id',
#         'in': 'path',
#         'required': True,
#         'description': 'Shop ID to fetch items for',
#         'schema': {'type': 'string'},
#     }],
#     responses={200: ItemSerializer(many=True)},
#     tags=["Items"]
# )
# @api_view(['GET'])
# # @has_perms
# def getItems(request, shop_id=""):
#     foods = Item.objects.filter(shop__id=request.shop_id)
#     serializer = ItemSerializer(foods, many=True)
#     return Response({"foods": serializer.data})


@extend_schema(responses={200: ItemSerializer(many=True)})
@api_view(["GET"])
# @has_perms(["can_view"])
def normalGetItems(request):
    foods = Item.objects.all()
    serializer = ItemSerializer(foods, many=True)
    return Response({"foods": serializer.data})


@extend_schema(
    parameters=[
        {
            "name": "id",
            "in": "query",
            "required": True,
            "description": "The ID of the item to retrieve.",
            "schema": {"type": "integer"},
        },
    ],
    responses={
        200: ItemSerializer,
        400: {"description": "Bad Request - Invalid or missing parameters"},
        404: {"description": "Not Found - Item does not exist"},
    },
)
@api_view(["GET"])
# @has_perms(["can_add"])
def getItem(request):
    item_id = request.GET.get("id")

    if not item_id:
        return Response(
            {"error": "The 'id' query parameter is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Convert item_id to integer and validate
        item_id = int(item_id)
    except ValueError:
        return Response(
            {"error": "The 'id' query parameter must be an integer."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        # Fetch the item from the database
        item = Item.objects.get(id=item_id)
        serializer = ItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Item.DoesNotExist:
        return Response(
            {"error": f"Item with id {item_id} not found."},
            status=status.HTTP_404_NOT_FOUND,
        )


@extend_schema(request=ItemSerializer, responses={201: ItemSerializer()})
@api_view(["POST"])
@has_perms(["can_update_bikes"], shop_required=True)
def createItem(request):
    data = request.data.copy()
    # Use the validated shop ID from the permission decorator
    data["shop"] = request.validated_shop_id
    serializer = ItemSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(
    request=ItemSerializer,
    responses={200: ItemSerializer()},
    summary="Update bike  requires[can_update_item]",
)
@api_view(["PUT"])
@has_perms(["can_update_item"], shop_required=True)
def updateItem(request, pk):
    try:
        # Only get items from the user's shop
        food = Item.objects.get(id=pk, shop_id=request.validated_shop_id)
    except Item.DoesNotExist:
        return Response(
            {"error": "Item not found or you don't have permission to update it"},
            status=404,
        )

    serializer = ItemSerializer(food, data=request.data)
    if serializer.is_valid():
        # Ensure the shop ID cannot be changed
        if "shop" in serializer.validated_data:
            serializer.validated_data["shop"] = food.shop
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)



@extend_schema(
    parameters=[OpenApiParameter(name="pk", type=OpenApiTypes.INT, location=OpenApiParameter.PATH)],
    responses={200: {"message": "Item deleted successfully"}},
    summary="Delete bike requires[can_delete_item]",
)
@api_view(["DELETE"])
@has_perms(["can_delete_item"], shop_required=True)
def deleteItem(request, pk: int):
    try:
        # Only get items from the user's shop
        item = Item.objects.get(id=pk, shop_id=request.validated_shop_id)
    except Item.DoesNotExist:
        return Response({"error": "Item not found or you don't have permission to delete it"}, status=404)
    
    item.delete()
    return Response({"message": "Item deleted successfully"}, status=200)



@extend_schema(
    responses={
        200: ItemSerializer(many=True),
    },
    description="Retrieve a list of recommended, popular, favorite, or featured items",
)
@api_view(["GET"])
def recommended(request):
    items = Item.objects.filter(
        Q(category="popular")
        | Q(category="recommended")
        | Q(category="favorate")
        | Q(category="featured")
    )
    serializer = ItemSerializer(items, many=True)
    return Response({"orders": serializer.data})


@extend_schema(
    parameters=[
        OpenApiParameter(
            name="q",
            type=OpenApiTypes.STR,
            description="Search query for item title or description",
        ),
        OpenApiParameter(
            name="category",
            type=OpenApiTypes.STR,
            description="Filter items by category",
        ),
    ],
    responses={
        200: ItemSerializer(many=True),
    },
    description="Search for items by query or category",
)
@api_view(["GET"])
@has_perms(["can_view"], shop_required=True)
def item_search_view(request):
    query = request.GET.get("q", None)
    category = request.GET.get("category", None)

    # Only search within the user's shop
    queryset = Item.objects.filter(shop_id=request.validated_shop_id)

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category:
        queryset = queryset.filter(category=category)

    serializer = ItemSerializer(queryset, many=True)
    return Response({"foods": serializer.data})





from rest_framework.permissions import IsAuthenticated


class SecificShopItems(APIView):

    permission_classes = [
        IsAuthenticated
    ]  # Ensure only authenticated users can access this view

    def get(self, request, format=None):
        # Extract `shop_id` from the request object
        shop_id = getattr(request, "shop_id", None)
        if not shop_id:
            return Response({"detail": "Shop ID is missing or invalid."}, status=400)

        # Retrieve items associated with the shop
        items = Item.objects.filter(shop_id=shop_id)
        serializer = ItemSerializer(items, many=True)

        # Return serialized data
        return Response({"foods": serializer.data})
