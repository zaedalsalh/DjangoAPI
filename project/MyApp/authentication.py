from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from MyApp.models import Userr

class UserrJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
            return Userr.objects.get(id=user_id)
        except Userr.DoesNotExist:
            return None
        


def superuser_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        return render(request, '403.html', status=403)
    return wrapper
