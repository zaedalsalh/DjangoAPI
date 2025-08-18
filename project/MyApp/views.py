from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, filters

from MyApp.models import Userr , UserRating , ServiceRequest , Notifications
from MyApp.serializers import UserrSerializer 



@api_view(['GET'])
def AllUserClint(request):
    Alluser = Userr.objects.filter(TypeOfService__in = [2,3,4])
    serializer = UserrSerializer( Alluser , many=True)
    return Response(serializer.data)


@api_view(['POST'])
def CreateUserClient(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
    '''
    {
  "FullName": "Zaid AlSalh",
  "Email": "zaid@example.com",
  "Password": "MyStrongPassword123",
  "TypeOfService": 1,
  "PhoneNumber": +62514145,
  "YearsOfExperience": 2,
  "Location": "edlib",
  "img": null,
  "IsNotifications": true,
  "IsServices": true
}
'''


@api_view(['POST'])
def CreateUser(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
    
    '''
{
    "FullName": "Zaid AlSalh",
    "Email": "zaid@example.com",
    "Password": "MyStrongPassword123",
    "TypeOfService": 1,
    "PhoneNumber": null,
    "YearsOfExperience": null,
    "Location": "",
    "img": null,
    "IsNotifications": true,
    "IsServices": False
}

    '''
    