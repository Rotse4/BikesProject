from django.urls import path
from . import views

urlpatterns = [
    path('', views.registration_view),
    path('viewUsers', views.viewUsers),
    path('adminLogin', views.adminLogin),
    path('userLogin', views.userLogin),
    path('select_shop', views.select_shop),
    path('getShopRoles/', views.ShopList.as_view()),
]

