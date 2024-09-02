# from shop.models import Shop
# from . models import Permission, Role, UserRole
# from django.contrib.auth.models import User

# # Assume you have a Shop instance
# shop_instance = Shop.objects.get(id=1)

# # Create Permissions
# view_permission = Permission.objects.create(name="Can view bikes", shop=shop_instance)
# edit_permission = Permission.objects.create(name="Can edit bikes", shop=shop_instance)
# delete_permission = Permission.objects.create(name="Can delete bikes", shop=shop_instance)

# # Create a Role and Assign Permissions
# manager_role = Role.objects.create(name="Manager")
# manager_role.permissions.add(view_permission, edit_permission, delete_permission)

# # Create a User and Assign a Role
# user_instance = User.objects.create_user(username='john_doe', password='password')
# user_role = UserRole.objects.create(user=user_instance, role=manager_role, name="John Doe", mobile_no="0712345678")


# Permisions = (
#         ('Manager', 'Maneger'),
#         ('Saff', 'Staff')

#     )

# @api_view(["POST"])
# def createPerm(request):
#     user = request.user
#     serializer = ShopSerializer(shops, many = True)
#     return Response({"shops":serializer.data})
    


from functools import wraps
from django.http import HttpResponseForbidden
from .models import *

def get_user_role(user):
    user_role= ShopUser.objects.get(user__id = user.id)
    return user_role.role

def has_permission(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                user_role = get_user_role(request.user)
                if user_role and user_role.permissions.filter(name=perm_name).exists():
                    return view_func(request, *args, **kwargs)
            return HttpResponseForbidden("You don't have permission to access this page.")
        return _wrapped_view
    return decorator