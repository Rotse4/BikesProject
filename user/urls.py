from django.urls import path
from . import views

urlpatterns = [
    path('', views.registration_view),
    # path('orderIt', views.createPerm),
]

