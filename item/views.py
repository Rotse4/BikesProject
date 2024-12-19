from django.shortcuts import render
from rest_framework.decorators import api_view, APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from account.permissions import has_perms
from .serializers import ItemSerializer
from .models import Item
from rest_framework import status
from django.db.models import Q


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
@has_perms(["can_view"])
def normalGetItems(request):
    foods = Item.objects.all()
    serializer = ItemSerializer(foods, many=True)
    return Response({"foods": serializer.data})


@extend_schema(
    parameters=[
        {
            "name": "pk",
            "in": "path",
            "required": True,
            "description": "Item ID",
            "schema": {"type": "integer"},
        }
    ],
    responses={200: ItemSerializer()},

)
@api_view(["GET"])
@has_perms(["can_view"])
def getItem(request, pk):
    try:
        food = Item.objects.get(id=pk)
        serializer = ItemSerializer(food)
        return Response(serializer.data)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)


@extend_schema(
    request=ItemSerializer, responses={201: ItemSerializer()}
)
@api_view(["POST"])
@has_perms(["can_add"], shop_required=True)
def createItem(request):
    data = request.data.copy()
    data["shop"] = request.shop_id
    print(f"shop id now {data['shop']}")
    serializer = ItemSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@extend_schema(
    request=ItemSerializer, responses={200: ItemSerializer()}
)
@api_view(["PUT"])
@has_perms(["can_edit"])
def updateItem(request, pk):
    try:
        food = Item.objects.get(id=pk)
    except Item.DoesNotExist:
        return Response({"error": "Item not found"}, status=404)

    serializer = ItemSerializer(food, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def recommended(request):
    items = ItemSerializer.objects.filter(
        Q(category="popular")
        | Q(category="recommended")
        | Q(category="favorate")
        | Q(category="featured")
    )
    serializer = ItemSerializer(items, many=True)
    return Response({"orders": serializer.data})


@api_view(["GET"])
def item_search_view(request):
    query = request.GET.get("q", None)
    category = request.GET.get("category", None)

    queryset = Item.objects.all()

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
    permission_classes = [IsAuthenticated]  # Ensure only authenticated users can access this view

    def get(self, request, format=None):
        # Extract `shop_id` from the request object
        shop_id = getattr(request, 'shop_id', None)
        if not shop_id:
            return Response({"detail": "Shop ID is missing or invalid."}, status=400)

        # Retrieve items associated with the shop
        items = Item.objects.filter(shop_id=shop_id)
        serializer = ItemSerializer(items, many=True)

        # Return serialized data
        return Response({"foods": serializer.data})
