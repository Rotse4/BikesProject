from functools import wraps
from rest_framework.response import Response
from shop.models import ShopUSer
from .models import Permission
from .serializers import PermissionSerializer


def get_user_role(account, shop_user):
    print(f"shop_user {shop_user}")
    try:
        # Ensure you're correctly querying the `ShopUser` model
        shop_user = ShopUSer.objects.get(id=shop_user)

        print(f"shop_user {shop_user.shop}")
        role = shop_user.role  # Return the actual role object
        shop = shop_user.shop
        print(f"shop_user {role} {shop}")

        return {"role": role, "shop": shop}
    except ShopUSer.DoesNotExist:
        print("shop user does not exist")
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
            role = None
            shop = None
            if request.account.is_authenticated:
                shop_user = getattr(request, "shop_user", None)
                print(f"shop_useer {shop_user}")
                if shop_user is not None:
                    user_role = get_user_role(request.account, request.shop_user)

                    role = user_role.get("role")
                    shop = user_role.get("shop")
                    print(f"shop is {shop}")
                    

                if role:
                    # Always verify that the role belongs to the current shop, regardless of shop_required
                    if role.shop_id != shop.id:
                        return Response(
                            f"This role {role} is not valid for this shop.",
                            status=403,
                        )
                    print(f"comparison {role.shop_id} and {shop.id}")
                    # If shop access is specifically required, do additional shop validation
                    if shop_required: 
                        shop_id = request.shop_id
                        if str(shop.id) != str(shop_id):
                            return Response(
                                "You don't have permission to access this shop.",
                                status=403,
                            )
                        # Store the validated shop ID for later use
                        request.validated_shop_id = shop.id
                        
                    # Check if the user has all the required permissions
                    missing_perms = [
                        perm
                        for perm in perm_names
                        if not role.permissions.filter(name=perm).exists()
                    ]
                    if not missing_perms:
                        # If shop access is required, validate the shop
                        if shop_required:
                            # Wrap the view function to validate items belong to the shop
                            response = view_func(request, *args, **kwargs)
                            
                            # If it's a Response object with data, verify items belong to shop
                            if isinstance(response, Response) and hasattr(response, 'data'):
                                data = response.data
                                # If it's a list of items
                                if isinstance(data, list) or (isinstance(data, dict) and 'foods' in data):
                                    items = data if isinstance(data, list) else data.get('foods', [])
                                    # Filter out items that don't belong to this shop
                                    filtered_items = [
                                        item for item in items
                                        if str(item.get('shop')) == str(shop.id)
                                    ]
                                    if isinstance(data, list):
                                        response.data = filtered_items
                                    else:
                                        response.data['foods'] = filtered_items
                                # If it's a single item
                                elif isinstance(data, dict) and 'shop' in data:
                                    if str(data['shop']) != str(shop.id):
                                        return Response(
                                            "You don't have permission to access this item.",
                                            status=403,
                                        )
                            return response

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
