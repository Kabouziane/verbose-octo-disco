from rest_framework import serializers
from .models import ServiceCategory, Service, Subscription, Appointment, SupportTicket, TicketMessage, ServiceReview

class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_with_vat = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Service
        fields = '__all__'

class SubscriptionSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)

    class Meta:
        model = Subscription
        fields = '__all__'

class AppointmentSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    staff_name = serializers.CharField(source='staff_member.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'

class TicketMessageSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)

    class Meta:
        model = TicketMessage
        fields = '__all__'

class SupportTicketSerializer(serializers.ModelSerializer):
    messages = TicketMessageSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.get_full_name', read_only=True)

    class Meta:
        model = SupportTicket
        fields = '__all__'

class ServiceReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    service_name = serializers.CharField(source='service.name', read_only=True)

    class Meta:
        model = ServiceReview
        fields = '__all__'