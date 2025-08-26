from rest_framework_simplejwt.authentication import JWTAuthentication
from MyApp.models import Userr

class UserrJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
            return Userr.objects.get(id=user_id)
        except Userr.DoesNotExist:
            return None