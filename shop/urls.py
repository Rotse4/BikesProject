from django.urls import path
from . import views


urlpatterns = [
    path('', views.shop_list),
    path('roles/create/', views.RoleCreateAPIView.as_view(), name='role_create_api'),
    path('roles/assign/', views.AssignRoleAPIView.as_view(), name='role_create_api'),
]