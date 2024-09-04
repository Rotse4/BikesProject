from django.urls import path
from . import views

urlpatterns = [
    path('', views.getItems),
    path('food/create/', views.createItem),
    # path('login', views.loginPage),
    path('food/<str:pk>/', views.getItem),
    path('food/<str:pk>/update/', views.updateItem),
    path('food/recommended', views.recommended),
    path('food/search', views.item_search_view),

    # path('foods/<int:pk>/', views.food_detail),
]