from django.urls import path
from . import views

urlpatterns = [
    path('', views.submit_order),
    path('orderIt', views.order_items),
    path('make_stk_push', views.make_stk_push),
    path('callback', views.mpesa_callback),
    path('delivered', views.delivered),
    path('userOrder', views.userOrder),
    path('rate', views.rate),
]

