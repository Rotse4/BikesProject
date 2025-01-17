from django.urls import path
from . import views

urlpatterns = [
    # path('shops/items', views.getItems),
     path('shops/allitems', views.normalGetItems),
    path('food/create/', views.createItem),
    path('bike/', views.getItem),
    path('food/<str:pk>/update/', views.updateItem),
    path('food/recommended', views.recommended),
    path('food/search', views.item_search_view),
    path('specificShopItems/', views.SecificShopItems.as_view()),

    # path('foods/<int:pk>/', views.food_detail),
]