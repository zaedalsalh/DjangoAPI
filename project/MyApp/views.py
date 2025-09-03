from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import get_object_or_404, redirect, render
from MyApp.models import EmailCode, Services

from django.utils import timezone
from datetime import timedelta

from rest_framework.response import Response
from rest_framework.decorators import api_view , authentication_classes



from MyApp.serializers import UserrSerializer  , NotificationsSerializer , UserRatingSerializer , Userr , UserRating , ServiceRequest , Notifications , ServiceRequestSerializer , ServicesSerializer

from rest_framework_simplejwt.tokens import RefreshToken

from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.conf import settings


from django.contrib.auth.hashers import make_password, check_password


from .authentication import UserrJWTAuthentication , superuser_required


@api_view(['GET'])
@authentication_classes([UserrJWTAuthentication])
def protected_view(request):
    user = request.user
    return Response({"message": f"مرحباً {user.FullName}"})


@api_view(['GET'])
def AllUserClint(request):
    all_users = Userr.objects.filter(TypeOfService__in=[2, 3, 4])
    serializer = UserrSerializer(all_users, many=True)
    Evaluation = UserRating.objects.all()

    data = []
    for user, serialized in zip(all_users, serializer.data):
        data.append({
            "id": serialized['id'],
            "FullName": serialized['FullName'],
            "Email": serialized['Email'],
            "PhoneNumber": serialized['PhoneNumber'],
            "YearsOfExperience": serialized['YearsOfExperience'],
            "Location": serialized['Location'],
            "img": serialized['img'],
            "IsServices": serialized['IsServices'],
            "TypeOfService": user.TypeOfService.ServiceName,
            'Evaluation':Evaluation.get(UserId=user.id).Evaluation if Evaluation.filter(UserId=user.id).exists() else None
        })

    return Response(data)


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
        results = Userr.objects.filter(TypeOfService__in=[2,3,4])

    serializer = UserrSerializer(results, many=True)
    data = []
    for user, serialized in zip(results, serializer.data):
        data.append({
            "id": serialized['id'],
            "FullName": serialized['FullName'],
            "Email": serialized['Email'],
            "PhoneNumber": serialized['PhoneNumber'],
            "YearsOfExperience": serialized['YearsOfExperience'],
            "Location": serialized['Location'],
            "img": serialized['img'],
            "IsServices": serialized['IsServices'],
            "TypeOfService": user.TypeOfService.ServiceName,
        })
    return Response(data)

@csrf_exempt
@api_view(['POST'])
def CreateUserClient(request):
    serializer = UserrSerializer(data=request.data)
    if serializer.is_valid():
        serializer.validated_data['Password'] = make_password(serializer.validated_data['Password'])
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
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
        serializer.validated_data['Password'] = make_password(serializer.validated_data['Password'])
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
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
                "user": user.data,
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
        if check_password(oldpassword, user.Password):
            user.Password = make_password(Newpassword)
            user.save()
            return Response({"RePassword":"تم التغيير"},status=200)
        else:
            return Response({"RePassword":"كلمة المرور غير صحيحة"},status=400)
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
@api_view(['PUT'])
def AcceptTheApplication(request, id):
    try:
        service = ServiceRequest.objects.get(id=id)
        service.ClientOrderStatus = 1
        service.save()
        Notifications.objects.filter(UserId__in=[service.IdUser.id, service.IdClient.id]).delete()
        
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



@api_view(['PUT'])
def RequestRejected(request, id):
    try:
        service = ServiceRequest.objects.get(id=id)
        service.ClientOrderStatus = 2
        Notifications.objects.filter(UserId__in=[service.IdUser.id, service.IdClient.id]).delete()

        notif_to_User = {
            "UserId": service.IdUser.id,
            "Title": "تم رفض طلبك",
            "Description": (
                f"عزيزي {service.IdUser.FullName}، "
                f"لقد قام {service.IdClient.FullName} برفض طلبك."
            ),
            "Isrequest": True
        }

        notif_serializer = NotificationsSerializer(data=notif_to_User)
        if notif_serializer.is_valid():
            notif_serializer.save()
        else:
            print("Notification Error:", notif_serializer.errors)


        return Response({"Ok": "تم رفض الطلب وحذف كل الإشعارات المرتبطة به"}, status=200)

    except ServiceRequest.DoesNotExist:
        return Response({"Error": "الطلب غير موجود"}, status=404)


@api_view(['GET'])
def selectServices(request):
    try:
        services = Services.objects.exclude(id=1)
        serializer = ServicesSerializer(services, many=True)
        return Response(serializer.data)
    except Services.DoesNotExist:
        return Response({"Error": "لا توجد خدمات متاحة"}, status=404)




from django.db.models import Count, Q

@superuser_required
def Index(request):
    user_counts = Userr.objects.aggregate(
        AllUserClint=Count('id', filter=Q(TypeOfService__in=[2, 3, 4])),
        AllUser=Count('id', filter=Q(TypeOfService=1)),
        AllUserClintJoiner=Count('id', filter=Q(TypeOfService=2)),
        AllUserClintBlacksmith=Count('id', filter=Q(TypeOfService=3)),
        AllUserClintElectrician=Count('id', filter=Q(TypeOfService=4)),
    )
    
    service_request_counts = ServiceRequest.objects.aggregate(
        TrueCount=Count('id', filter=Q(ClientOrderStatus=1)),
        FalseCount=Count('id', filter=Q(ClientOrderStatus=2)),
    )

    chart_data = [
        user_counts['AllUserClintJoiner'],
        user_counts['AllUserClintBlacksmith'],
        user_counts['AllUserClintElectrician']
    ]

    userrating = list(
        UserRating.objects.filter(
            Evaluation__range=(1, 5),
            UserId__TypeOfService__in=[2, 3, 4]
        ).values(
            'id',
            'UserId__FullName',
            'UserId__Email',
            'Evaluation'
        ).order_by('Evaluation').reverse()
    )
    AllUserClintUser = Userr.objects.filter(TypeOfService__in=[2, 3, 4])
    all_services = Services.objects.exclude(id=1)
    allServiceRequest = ServiceRequest.objects.all()
    AllNotifications = Notifications.objects.all()

    return render(request, 'home.html', {
        "counterAllUserClint": user_counts['AllUserClint'],
        "counterAllUser": user_counts['AllUser'],
        "counterAllServiceRequestTrue": service_request_counts['TrueCount'],
        "counterAllServiceRequestFalse": service_request_counts['FalseCount'],
        "chart_data": chart_data,  
        "userrating": userrating,
        "AllUserClintUser": AllUserClintUser,
        "all_services": all_services,
        "allServiceRequest": allServiceRequest,
        'AllNotifications':AllNotifications,
    })

def deleteuser(request , id_user):
    user = Userr.objects.get(id = id_user)
    user.delete()
    return redirect('/index/#users')

def adduser(request):
    if request.method == 'POST':
        data = request.POST.copy()
        data['Password'] = make_password(data.get('Password'))
        user = UserrSerializer(data=data)
        if user.is_valid():
            userSaveed = user.save()

            refresh = RefreshToken.for_user(userSaveed)
            access_token = str(refresh.access_token)

            UserRating.objects.create(
                UserId = userSaveed,
                Evaluation = 1.0
            )
            

        return redirect('/index/#users')
    else:
        return redirect('/index/#users')


def AddNotification(request):
    if request.method == 'POST':
        data = request.POST.copy()

        user_id = data.get('UserId')
        title = data.get('Title')
        description = data.get('Description')

        if user_id == 'AllUser':
            users = Userr.objects.all()
            notifications = [
                Notifications(
                    UserId=user,
                    Title=title,
                    Description=description,
                    Isrequest=False
                ) for user in users
            ]
            Notifications.objects.bulk_create(notifications)  # create all notifications
        else:
            user = get_object_or_404(Userr, id=user_id)
            Notifications.objects.create(
                UserId=user,
                Title=title,
                Description=description,
                Isrequest=False
            )

        return redirect('/index/#notifications')

    return redirect('/index/#notifications')
