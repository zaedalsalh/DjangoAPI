from rest_framework import serializers
from .models import Userr, UserRating, Notifications, ServiceRequest


class NotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifications
        fields = '__all__'


class ServiceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'


class UserrSerializer(serializers.ModelSerializer):
    notifications = NotificationsSerializer(source='notifications_set', many=True, read_only=True)
    requests_made = ServiceRequestSerializer(many=True, read_only=True)
    requests_received = ServiceRequestSerializer(many=True, read_only=True)

    class Meta:
        model = Userr
        fields = '__all__'
