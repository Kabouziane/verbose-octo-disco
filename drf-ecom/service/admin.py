from django.contrib import admin
from .models import ServiceCategory, Service, Subscription, Appointment, SupportTicket, ServiceReview

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'type', 'price', 'is_active']
    list_filter = ['category', 'type', 'is_active']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['service', 'customer', 'appointment_date', 'status']
    list_filter = ['status', 'service']

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'customer', 'subject', 'priority', 'status']
    list_filter = ['priority', 'status']