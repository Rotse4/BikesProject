from django.urls import path
from . import views

urlpatterns = [
    path('', views.registration_view),
    path('viewUsers', views.viewUsers),
    path('adminLogin', views.adminLogin),
    path('userLogin', views.userLogin),
    path('select_shop', views.select_shop),
     path('search_user', views.search_user_by_phone),
    path('getShopRoles/', views.ShopList.as_view()),
]
