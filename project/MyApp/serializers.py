from rest_framework import serializers
from .models import Userr, UserRating, Notifications, ServiceRequest , Services


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        exclude = ['id']


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        exclude = ['id']


class UserrSerializer(serializers.ModelSerializer):
    notifications = NotificationsSerializer(source='notifications_set', many=True, read_only=True)
    requests_made = ServiceRequestSerializer(many=True, read_only=True)
    requests_received = ServiceRequestSerializer(many=True, read_only=True)

    class Meta:
        model = Userr
        fields = '__all__'


class UserRatingSerializer(serializers.ModelSerializer):
    user = UserrSerializer(source='UserId', read_only=True)
    class Meta:
        model = UserRating
        exclude = ['id' , 'UserId']
        
class ServicesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Services
        fields = '__all__'