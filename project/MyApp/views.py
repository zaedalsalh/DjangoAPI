from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.decorators import api_view , permission_classes
from rest_framework.permissions import IsAuthenticated


from MyApp.serializers import UserrSerializer  , NotificationsSerializer , UserRatingSerializer , Userr , UserRating , ServiceRequest , Notifications

from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings




@api_view(['GET'])
# @permission_classes([IsAuthenticated])
def AllUserClint(request):
    Alluser = Userr.objects.filter(TypeOfService__in = [2,3,4])
    serializer = UserrSerializer( Alluser , many=True)
    return Response(serializer.data)


@api_view(['POST'])
def CreateUserClient(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        
        notification_data = {
        "UserId": user.id,
        "Title": f" {user.FullName} مرحباً بالعميل",
        "Description": "نرحب بك في تطبيقنا. نتمنى لك تجربة رائعة مع خدماتنا.",
        "Isrequest": False
                        }
        
        UserRating.objects.create(
            UserId = user,
            Evaluation = 0.0
        )
        
        notif_serializer = NotificationsSerializer(data=notification_data)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            pass

        return Response(serializer.data, status=201)
    else:
        return Response(serializer.errors, status=400)
    '''
{
  "FullName": "Ahmad Ali",
  "Email": "ahmad@example.com",
  "Password": "securepassword123",
  "TypeOfService": 2,
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
  "TypeOfService": 1
}


    '''

'''
B-Tree index → البحث = O(log n) (n = عدد المستخدمين).
Hash index → البحث = O(1) تقريبًا للمطابقة التامة.
'''
@api_view(['POST'])
def Login(request):
    try:
        user = Userr.objects.get(Email = request.data.get('Email'))
        if user.Password == request.data.get('Password'):
            # jwt
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
        else:
             return Response({"error": "كلمة المرور غير صحيحة"}, status=401)
    except Userr.DoesNotExist:
        return Response({"error": "البريد الإلكتروني غير صحيحة"}, status=401)


'''
{
  "Email": "ahmad@example.com",
  "Password": "securepassword123"
}
'''


@api_view(['POST'])
def refresh_access(request):
    refresh_token = request.data.get('refresh')
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)
        return Response({"access": access_token})
    except Exception:
        return Response({"error": "Invalid refresh token"}, status=401)
    
'''
{
"refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1NjM3OTMxNSwiaWF0IjoxNzU1Nzc0NTE1LCJqdGkiOiJhMjkwNGEwOTUxYTM0ZGM5OGI0ZWE3Yjg1YTVlZjU3YiIsInVzZXJfaWQiOiI0In0.3C7VYIjRaxlvISt__Z_6_6V486RiUXktfjisvMOv3zE"
}
'''
    

@api_view(['POST'])
def send_code_to_email(request):
    email = request.data.get("Email")

    if email == '':
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
    
    
    
@api_view(['POST'])
def rePassword(request):
    email = request.data.get("Email")
    oldpassword = request.data.get("OldPassword")
    Newpassword = request.data.get("NewPassword")
    if oldpassword == Newpassword:
        return Response({"RePassword":"كلمة المرور الجديدة نفسها القديمة "},status=400)
    try:
        user = Userr.objects.get(Email = email)
        user.Password = Newpassword
        user.save()
        return Response({"RePassword":"تم التغيير"},status=200)
    except Userr.DoesNotExist:
        return Response({"RePassword":"كلمة المرور غير صحيحة"},status=400)

'''
{
"Email":"ahmad@example.com",
"OldPassword":"securepassword123",
"NewPassword":"securepassword123"
}
'''

@api_view(['PUT'])
def reIsNotifications(request,id):
    bool_value = str(request.data.get('IsNotifications')).lower() == 'true'
    updated = Userr.objects.filter(id=id).update(IsNotifications=bool_value)
    if updated:
        return Response({"Ok": "تم تغيير الحالة"}, status=200)
    else:
        return Response({"Error": "لم يتم العثور على المستخدم"}, status=400)

# {"IsNotifications":"True"}

@api_view(['PUT'])
def reIsServices(request,id):
    bool_value = str(request.data.get('IsServices')).lower() == 'true'
    updated = Userr.objects.filter(id=id).update(IsServices=bool_value)
    if updated:
        return Response({"Ok": "تم تغيير الحالة"}, status=200)
    else:
        return Response({"Error": "لم يتم العثور على المستخدم"}, status=400)


# {"IsServices":"True"}

@api_view(['GET'])
def moviesWithRatings(request):
    userrating = UserRating.objects.filter(Evaluation__range=(3.5, 5) , UserId__TypeOfService__in=[2, 3, 4])
    userrating = UserRatingSerializer(userrating , many=True)
    return Response(userrating.data)


@api_view(['PUT'])
def updateUserRating(request, UserId):
    Evaluation = request.data.get('Evaluation')
    try:
        user = UserRating.objects.get(UserId = UserId)
        user.Evaluation = round((user.Evaluation + Evaluation) / 2, 2)
        user.save()
        return Response({"OK":"تم تقييم المستخدم"}) 
    except UserRating.DoesNotExist:
        return Response({"Error":"لم يجد المستخدم المراد تقييمة"}) 
    
'''
{
    "Evaluation": 4
}
'''


