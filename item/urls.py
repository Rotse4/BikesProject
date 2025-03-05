from django.urls import path
from . import views

urlpatterns = [
    # path('shops/items', views.getItems),
     path('shops/allitems', views.normalGetItems),
    path('bike/create/', views.createItem),
    path('bike/', views.getItem),
    path('bike/<str:pk>/update/', views.updateItem),
    path('bike/recommended', views.recommended),
    path('bike/search', views.item_search_view),
    path('bike/deleteItem', views.deleteItem),
    path('specificShopItems/', views.SecificShopItems.as_view()),

    # path('foods/<int:pk>/', views.food_detail),
]