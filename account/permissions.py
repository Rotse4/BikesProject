
from functools import wraps
from django.http import HttpResponseForbidden

from shop.models import ShopUSer
from .models import *
from rest_framework.response import Response

def get_user_role(account):
    try:
        shop_user = ShopUSer.objects.get(user__id=account.id)
        role = shop_user.role
        shop = shop_user.shop

        access = {"role": role, "shop": shop}
        print(f"Shop: {shop}")
        return access
    except ShopUSer.DoesNotExist:
        # Return an empty dictionary or handle it in a consistent way
        return {"role": None, "shop": None}




def has_perms(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            print(str(request.account) + "yyy")
            if request.account.is_authenticated:
                print("here")
                user_role = get_user_role(request.account)
                
                # Check if role is valid and has permissions
                role = user_role.get("role")
                if role and role.permissions.filter(name=perm_name).exists():
                    return view_func(request, *args, **kwargs)
                
            return Response("You don't have permission to access this page.")
        return _wrapped_view
    return decorator
