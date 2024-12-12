from functools import wraps
from rest_framework.response import Response
from shop.models import ShopUSer
from .models import Permission
from .serializers import PermissionSerializer


def get_user_role(account, shop_user):
    try:
        shop_user = ShopUSer.objects.get(id=account.id)
        print(f"shop_user {shop_user}")
        role = shop_user.role
        shop = shop_user.shop
        print(f"shop_user {role} {shop}")

        return {"role": role, "shop": shop}
    except ShopUSer.DoesNotExist:
        print(f"shop_user does not exist")
        return {"role": None, "shop": None}


def has_perms(perm_names, shop_required=False):
    """
    A decorator to check if the user has all required permissions.

    Args:
        perm_names (list): A list of permission names that the user must have.
        shop_required (bool): Whether access to the shop is required.
    """
    if isinstance(perm_names, str):
        perm_names = [perm_names]  # Ensure it's a list for uniform handling

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            role = None  # Initialize role to avoid UnboundLocalError
            shop = None  # Initialize shop to avoid UnboundLocalError
            if request.account.is_authenticated:
                shop_user = getattr(request, "shop_user", None)
                if shop_user is not None:
                    user_role = get_user_role(request.account, request.shop_user)

                    role = user_role.get("role")
                    shop = user_role.get("shop")

                if role:
                    # Check if the user has all the required permissions
                    missing_perms = [
                        perm
                        for perm in perm_names
                        if not role.permissions.filter(name=perm).exists()
                    ]
                    if not missing_perms:
                        # If shop access is required, validate the shop
                        if shop_required:
                            shop_id = request.shop_id
                            print(f"shop_id {shop_id}")
                            if str(shop.id) == str(shop_id):
                                return view_func(request, *args, **kwargs)
                            else:
                                return Response(
                                    "You don't have permission to access this shop.",
                                    status=403,
                                )
                        else:
                            return view_func(request, *args, **kwargs)

                # If any required permission is missing
                return Response(
                    "You don't have access permission.",
                    status=403,
                )

            return Response(
                "You don't have permission to access this page.", status=403
            )

        return _wrapped_view

    return decorator
