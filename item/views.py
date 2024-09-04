from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . serializers import ItemSerializer
from . models import Item
from rest_framework import status
from django.db.models import Q

# Create your views here.
    
@api_view(['GET'])
# @permission_classes((IsAuthenticated,))
def getItems(request):
    foods= Item.objects.all()
    serializer = ItemSerializer(foods, many = True)
    return Response({
        "foods":serializer.data
    })

@api_view(['GET',])
def getItem(request, pk):
    food= Item.objects.get(id=pk)
    serializer = ItemSerializer(food, many = False)
    return Response(serializer.data)



@api_view(['POST'])
def createItem(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        food = serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

@api_view(['PUT'])
def updateItem(request, pk):
    try:
        food = Item.objects.get(id=pk)
    except Item.DoesNotExist:
        return Response({'error': 'Food item not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ItemSerializer(food, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
@api_view(['GET'])
def recommended(request):
    items = ItemSerializer.objects.filter(Q(category='popular') | Q(category='recommended') 
                                | Q(category='favorate')
                                | Q(category='featured'))
    serializer = ItemSerializer(items, many=True)
    return Response({"orders":serializer.data})


@api_view(['GET'])
def item_search_view(request):
    query = request.GET.get('q', None)
    category = request.GET.get('category', None)

    queryset = Item.objects.all()

    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category:
        queryset = queryset.filter(category=category)

    serializer = ItemSerializer(queryset, many=True)
    return Response({"foods":serializer.data})