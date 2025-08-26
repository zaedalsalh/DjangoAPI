from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render
from MyApp.models import EmailCode

from django.utils import timezone
from datetime import timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view , authentication_classes



from MyApp.serializers import UserrSerializer  , NotificationsSerializer , UserRatingSerializer , Userr , UserRating , ServiceRequest , Notifications , ServiceRequestSerializer

from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings


from django.contrib.auth.hashers import make_password, check_password


from .authentication import UserrJWTAuthentication 


@api_view(['GET'])
@authentication_classes([UserrJWTAuthentication])
def protected_view(request):
    user = request.user
    return Response({"message": f"مرحباً {user.FullName}"})



@api_view(['GET'])
def AllUserClint(request):
    Alluser = Userr.objects.filter(TypeOfService__in = [2,3,4])
    serializer = UserrSerializer( Alluser , many=True)
    return Response(serializer.data)

@api_view(['GET'])
def AllClintTypeOfService(request , Type):
    if Type == 1:
        return Response({"Error":"هذا مستخدم وليس عميل"})
    Alluser = Userr.objects.filter(TypeOfService = Type)
    serializer = UserrSerializer( Alluser , many=True)
    return Response(serializer.data)



@api_view(['POST'])
def SearchClint(request):
    FullName = request.data.get('FullName' , '')
    Type = request.data.get('Type')
    if FullName and Type:
        results = Userr.objects.filter(FullName__icontains=FullName, TypeOfService_id=Type)
    elif FullName:
        results = Userr.objects.filter(FullName__icontains=FullName, TypeOfService__in=[2,3,4])
    else:
        return Response({"error": "الرجاء إدخال الاسم للبحث"}, status=400)

    serializer = UserrSerializer(results, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
def CreateUserClient(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.Password = make_password(user.Password)
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user.save()
        
        
        notification_data = {
        "UserId": user.id,
        "Title": f" {user.FullName} مرحباً بالعميل",
        "Description": "نرحب بك في تطبيقنا. نتمنى لك تجربة رائعة مع خدماتنا.",
        "Isrequest": False
                        }
        
        UserRating.objects.create(
            UserId = user,
            Evaluation = 1.0
        )
        
        notif_serializer = NotificationsSerializer(data=notification_data)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            pass

        return Response({
            "user": serializer.data,
            "tokens": {
                'refresh': str(refresh),
                'access': access_token
            }
        }, status=201)
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

@csrf_exempt
@api_view(['POST'])
def CreateUser(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.Password = make_password(user.Password)
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        user.save()
        
        notification_data = {
            "UserId": user.id,
            "Title": f" مرحباً {user.FullName}",
            "Description": "نرحب بك في تطبيقنا. نتمنى لك تجربة رائعة.",
            "Isrequest": False
        }
        notif_serializer = NotificationsSerializer(data=notification_data)
        if notif_serializer.is_valid():
            notif_serializer.save()
            
        else:
            print(notif_serializer.errors)

        return Response({
            "user": serializer.data,
            "tokens": {
                'refresh': str(refresh),
                'access': access_token
            }
        }, status=201)
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
        if check_password(request.data.get('Password'), user.Password):
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
def sendCodeToEmail(request):
    email = request.data.get("Email")

    if not email:
        return Response({"error": "يجب إدخال البريد الإلكتروني"}, status=400)

    try:
        user = Userr.objects.get(Email=email)
    except Userr.DoesNotExist:
        return Response({"error": "البريد الإلكتروني غير مسجل"}, status=404)

    code = get_random_string(length=6, allowed_chars='0123456789')

    obj, created = EmailCode.objects.get_or_create(
        email=email,
        defaults={
            "code": code,
            "expires_at": timezone.now() + timedelta(minutes=5)
        }
    )

    if not created:
        obj.code = code
        obj.expires_at = timezone.now() + timedelta(minutes=5)
        obj.save()

    send_mail(
        subject="رمز التحقق",
        message=f"مرحباً {user.FullName}, رمز التحقق الخاص بك هو: {code}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

    return Response({
        "message": "تم إرسال رمز التحقق إلى البريد الإلكتروني.",
    }, status=200)

    
@api_view(['POST'])
def verifyCode(request):
    email = request.data.get("Email")
    code = request.data.get("Code")

    if not email or not code:
        return Response({"error": "البريد الإلكتروني والرمز مطلوبان"}, status=400)

    try:
        record = EmailCode.objects.filter(
            email=email,
            code=code,
            is_used=False,
            expires_at__gt=timezone.now()
        ).latest("created_at")
    except EmailCode.DoesNotExist:
        return Response({"error": "رمز غير صالح أو منتهي الصلاحية"}, status=400)

    record.delete()

    return Response({"message": "تم التحقق بنجاح"}, status=200)



@api_view(['POST'])
def rePassword(request):
    email = request.data.get("Email")
    oldpassword = request.data.get("OldPassword")
    Newpassword = request.data.get("NewPassword")
    if oldpassword == Newpassword:
        return Response({"RePassword":"كلمة المرور الجديدة نفسها القديمة "},status=400)
    try:
        user = Userr.objects.get(Email = email)
        user.Password = make_password(Newpassword)
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

@api_view(['GET'])
def getUserAndClientById(request , id):
    try:
        user = Userr.objects.get(id = id)
        serializer = UserrSerializer(user)
        data = serializer.data
        if (data['TypeOfService']) == 1 :
            data.pop('requests_made', None)
            data.pop('requests_received', None)
            return Response(data , status=200)
        else:
            return Response(data , status=200)    
    except Userr.DoesNotExist:
        return Response({"Error":"المستخدم غير موجود"})
    

@api_view(['PUT'])
def updateUser(request):
    try:
        id_user = request.data.get('id')
        user = Userr.objects.get(id = id_user)
        user = UserrSerializer(user , data = request.data , partial=True)
        if user.is_valid():
            user.save()
            return Response(user.data , status=200)
        else:
            return Response(user.errors , status=400)
    except Userr.DoesNotExist:
        return Response({"Error":"لم يتم ايجاد المستخدم"} , status=404)


'''
بامكانك تضيف الحقل الي بدك ياه
{
  "id": 1,
  "FullName": "Ahmad Ali",
  "TypeOfService": 4,
  "PhoneNumber": 1000000000,
  "YearsOfExperience": 5,
  "Location": "Beirut, Lebanon",
  "IsNotifications": true,
  "IsServices": true
}

'''

@api_view(['DELETE'])
def deleteUser(request, id_user):
    try:
        user = Userr.objects.get(id=id_user)
        user.delete()
        return Response({"Ok": "تم حذف المستخدم بنجاح"}, status=200)
    except Userr.DoesNotExist:
        return Response({"error": "المستخدم غير موجود"}, status=404)

@api_view(['POST'])
def addService(request):
    serializer = ServiceRequestSerializer(data=request.data)

    if serializer.is_valid():
        service = serializer.save()
        
        notif_to_User = {
            "UserId": service.IdUser.id,
            "Title": "تم إرسال طلبك بنجاح",
            "Description": (
                f"عزيزي {service.IdUser.FullName}، "
                f"لقد تم إرسال طلبك إلى {service.IdClient.FullName}. "
                "سوف يتم إشعارك فور قيام العميل بقبول أو رفض الطلب. "
            ),
            "Isrequest": False
        }
        notifUser = NotificationsSerializer(data=notif_to_User)
        if notifUser.is_valid():
            notifUser.save()

            notif_to_Client = {
                "UserId": service.IdClient.id,
                "Title": "لديك طلب جديد",
                "Description": (
                    f"عزيزي {service.IdClient.FullName}، "
                    f"لقد استلمت طلباً جديداً من {service.IdUser.FullName}. "
                    "يرجى مراجعة تفاصيل الطلب لاتخاذ الإجراء المناسب (قبول أو رفض)."
                ),
                "Isrequest": False
            }
            notifClient = NotificationsSerializer(data=notif_to_Client)
            if notifClient.is_valid():
                notifClient.save()
            else:
                print("Notification (client) errors:", notifClient.errors)

        else:
            print("Notification (user) errors:", notifUser.errors)

        return Response(serializer.data, status=201)

    else:
        return Response(serializer.errors, status=400)

{
    "IdUser":"1",
    "IdClient":"4",
    "Location":"سوريا - ادلب ",
    "HourlyPrice":"5"
}
@api_view(['GET'])
def AcceptTheApplication(request, id):
    try:
        service = ServiceRequest.objects.get(id=id)
        service.ClientOrderStatus = True
        service.save()
        
        notif_to_User = {
            "UserId": service.IdUser.id,
            "Title": "تم قبول طلبك",
            "Description": (
                f"عزيزي {getattr(service.IdUser, 'FullName', service.IdUser.FullName)}, "
                f"لقد تم قبول طلبك من قبل {getattr(service.IdClient, 'FullName', service.IdClient.FullName)}."
            ),
            "Isrequest": True
        }

        notif_serializer = NotificationsSerializer(data=notif_to_User)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            print("Notification Error:", notif_serializer.errors)

        return Response({"Ok": "تم قبول الطلب"}, status=200)

    except ServiceRequest.DoesNotExist:
        return Response({"Error": "الطلب غير موجود"}, status=404)



@api_view(['DELETE'])
def Terminado(request, id):
    try:
        service = ServiceRequest.objects.get(id=id)
        Notifications.objects.filter(UserId__in=[service.IdUser.id, service.IdClient.id]).delete()
        service.delete()
        return Response({"OK":"تم حذف كلشي"},status=200)

    except ServiceRequest.DoesNotExist:
        return Response({"Error": "الطلب غير موجود"}, status=404)

