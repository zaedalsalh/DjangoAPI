from django.contrib import admin
from django.urls import path
from MyApp import views

# JWT
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('AllClintByTypeOfService/<int:Type>' ,  views.AllClintTypeOfService),
    path('SearchClint/' ,  views.SearchClint),
    path('AllUserClint/' ,  views.AllUserClint),
    path('CreateUserClint/' ,  views.CreateUserClient),
    path('CreateUser/' ,  views.CreateUser),
    path('repassword/' ,  views.rePassword),
    path('reIsNotifications/<int:id>/' ,  views.reIsNotifications),
    path('reIsServices/<int:id>/' ,  views.reIsServices),
    path('moviesWithRatings/' ,  views.moviesWithRatings),
    path('updateUserRating/<int:UserId>' ,  views.updateUserRating),
    path('getUserAndClientById/<int:id>' ,  views.getUserAndClientById),
    path('updateUser/' ,  views.updateUser),
    path('deleteUser/<int:id_user>' ,  views.deleteUser ,),
    path('addService/' ,  views.addService),
    path('AcceptTheApplication/<int:id>' ,  views.AcceptTheApplication),

    # jwt
    path('login/' , views.Login),
    path('refresh-access/', views.refresh_access),
    path('protected_view/', views.protected_view),
    
    path('sendCodeToEmail/', views.sendCodeToEmail),
    path('verifyCode/', views.verifyCode),

    path('RequestRejected/<int:id>' ,  views.RequestRejected),
    
    path('selectServices/' ,  views.selectServices),
    
    # templates
    path('index/', views.Index, name='index'),
    path('deleteuser/<int:id_user>', views.deleteuser,  name='deleteuser'),
    path('AddUser/', views.adduser,  name='AddUser'),
    path('AddNotification/', views.AddNotification,  name='AddNotification'),
]
