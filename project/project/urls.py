from django.contrib import admin
from django.urls import path
from MyApp import views

# JWT
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('AllUserClint/' ,  views.AllUserClint),
    path('CreateUserClint/' ,  views.CreateUserClient),
    path('CreateUser/' ,  views.CreateUser),
    path('repassword/' ,  views.rePassword),
    path('reIsNotifications/<int:id>/' ,  views.reIsNotifications),
    path('reIsServices/<int:id>/' ,  views.reIsServices),
    
    # jwt
    path('login/' , views.Login),
    path('refresh-access/', views.refresh_access),
    
    path('send_code_to_email/', views.send_code_to_email),
]
