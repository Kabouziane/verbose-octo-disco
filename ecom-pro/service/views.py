from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta

from .models import ServiceCategory, Service, Subscription, Appointment, SupportTicket, TicketMessage, ServiceReview
from .serializers import (
    ServiceCategorySerializer, ServiceSerializer, SubscriptionSerializer,
    AppointmentSerializer, SupportTicketSerializer, TicketMessageSerializer,
    ServiceReviewSerializer
)
from shop.models import Customer

class ServiceCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    permission_classes = [AllowAny]

class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    permission_classes = [AllowAny]
    filterset_fields = ['category', 'type']
    search_fields = ['name', 'description']

    @action(detail=True, methods=['get'])
    def available_slots(self, request, pk=None):
        service = self.get_object()
        date_str = request.query_params.get('date')
        
        if not date_str:
            return Response({'error': 'Date parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Logique simplifiée pour les créneaux disponibles
        start_time = datetime.combine(date, datetime.min.time().replace(hour=9))
        end_time = datetime.combine(date, datetime.min.time().replace(hour=17))
        
        slots = []
        current_time = start_time
        
        while current_time < end_time:
            # Vérifier si le créneau est libre
            is_available = not Appointment.objects.filter(
                service=service,
                appointment_date=current_time,
                status__in=['scheduled', 'confirmed']
            ).exists()
            
            if is_available:
                slots.append(current_time.strftime('%H:%M'))
            
            current_time += timedelta(minutes=service.duration_minutes or 60)
        
        return Response({'available_slots': slots})

class SubscriptionViewSet(viewsets.ModelViewSet):
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Subscription.objects.filter(customer=customer)

    @action(detail=True, methods=['post'])
    def pause(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'paused'
        subscription.save()
        return Response({'status': 'paused'})

    @action(detail=True, methods=['post'])
    def resume(self, request, pk=None):
        subscription = self.get_object()
        subscription.status = 'active'
        subscription.save()
        return Response({'status': 'resumed'})

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Appointment.objects.filter(customer=customer)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        
        # Vérifier si l'annulation est possible (ex: 24h avant)
        if appointment.appointment_date - timezone.now() < timedelta(hours=24):
            return Response(
                {'error': 'Cannot cancel appointment less than 24 hours in advance'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = 'cancelled'
        appointment.save()
        return Response({'status': 'cancelled'})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        appointment = self.get_object()
        new_date = request.data.get('new_date')
        
        if not new_date:
            return Response({'error': 'New date required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_datetime = datetime.fromisoformat(new_date)
            appointment.appointment_date = new_datetime
            appointment.save()
            return Response({'status': 'rescheduled', 'new_date': new_datetime})
        except ValueError:
            return Response({'error': 'Invalid date format'}, status=status.HTTP_400_BAD_REQUEST)

class SupportTicketViewSet(viewsets.ModelViewSet):
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return SupportTicket.objects.filter(customer=customer)

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, user=self.request.user)
        # Générer un numéro de ticket unique
        ticket_number = f"TK{timezone.now().strftime('%Y%m%d')}{SupportTicket.objects.count() + 1:04d}"
        serializer.save(customer=customer, ticket_number=ticket_number)

    @action(detail=True, methods=['post'])
    def add_message(self, request, pk=None):
        ticket = self.get_object()
        message_text = request.data.get('message')
        
        if not message_text:
            return Response({'error': 'Message required'}, status=status.HTTP_400_BAD_REQUEST)
        
        message = TicketMessage.objects.create(
            ticket=ticket,
            author=request.user,
            message=message_text
        )
        
        serializer = TicketMessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ServiceReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return ServiceReview.objects.filter(customer=customer)

    def perform_create(self, serializer):
        customer = get_object_or_404(Customer, user=self.request.user)
        serializer.save(customer=customer)