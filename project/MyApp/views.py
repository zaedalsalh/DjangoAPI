from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated


from MyApp.models import Userr , UserRating , ServiceRequest , Notifications
from MyApp.serializers import UserrSerializer  , NotificationsSerializer

from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings




@api_view(['GET'])

def AllUserClint(request):
    Alluser = Userr.objects.filter(TypeOfService__in = [2,3,4])
    serializer = UserrSerializer( Alluser , many=True)
    return Response(serializer.data)


@api_view(['POST'])
def CreateUserClient(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        full_name = user.FullName
        notification_data = {
        "UserId": user.id,
        "Title": f" {full_name} مرحباً بالعميل",
        "Description": "نرحب بك في تطبيقنا. نتمنى لك تجربة رائعة مع خدماتنا.",
        "Isrequest": False
                        }

        notif_serializer = NotificationsSerializer(data=notification_data)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            print(notif_serializer.errors)

        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
    '''
{
  "FullName": "Ahmad Ali",
  "Email": "ahmad@example.com",
  "Password": "securepassword123",
  "TypeOfService": 1,
  "PhoneNumber": 1234567890,
  "YearsOfExperience": 5,
  "Location": "Damascus",
  "IsNotifications": true,
  "IsServices": true
}

'''


@api_view(['POST'])
def CreateUser(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        full_name = user.FullName
        
        notification_data = {
            "UserId": user.id,
            "Title": f"{full_name} مرحباً",
            "Description": "نرحب بك في تطبيقنا. نتمنى لك تجربة رائعة.",
            "Isrequest": False
        }
        notif_serializer = NotificationsSerializer(data=notification_data)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            print(notif_serializer.errors)

        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)

    '''
{
  "FullName": "Ahmad Ali",
  "Email": "ahmad@example.com",
  "Password": "securepassword123",
  "TypeOfService": 1,
  "PhoneNumber": 1234567890,
  "YearsOfExperience":,
  "Location": "",
  "IsNotifications": true,
  "IsServices": true
}


    '''

@api_view(['POST'])
def Login(request):
    try:
        user = Userr.objects.get(Email = request.data.get('Email') , Password = request.data.get('Password') )
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user = UserrSerializer(user)
        
        
        return Response({
            "id": user.data['id'],
            "FullName": user.data['FullName'],
            "TypeOfService": user.data['TypeOfService'],
            "refresh": str(refresh),
            "access": access_token
        })
    except Userr.DoesNotExist:
        return Response({"error": "البريد الإلكتروني أو كلمة المرور غير صحيحة"}, status=401)



@api_view(['POST'])
def refresh_access(request):
    refresh_token = request.data.get('refresh')
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return Response({"access": access_token})
    except Exception:
        return Response({"error": "Invalid refresh token"}, status=401)
    
    
    

@api_view(['POST'])
def send_code_to_email(request):
    email = request.data.get("Email")

    if not email:
        return Response({"error": "يجب إدخال البريد الإلكتروني"}, status=400)

    try:
        user = Userr.objects.get(Email=email)
    except Userr.DoesNotExist:
        return Response({"error": "البريد الإلكتروني غير مسجل"}, status=404)

    code = get_random_string(length=6, allowed_chars='0123456789')

 
    send_mail(
        subject="رمز التحقق",
        message=f"مرحباً {user.FullName}, رمز التحقق الخاص بك هو: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({
        "message": "تم إرسال رمز التحقق إلى البريد الإلكتروني.",
        "code": code 
    }, status=200)