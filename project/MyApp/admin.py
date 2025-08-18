from django.contrib import admin
from MyApp.models import Userr , Services , UserRating , ServiceRequest , Notifications

admin.site.register(Userr)
admin.site.register(Services)
admin.site.register(UserRating)
admin.site.register(ServiceRequest)
admin.site.register(Notifications)