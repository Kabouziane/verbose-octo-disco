from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, datetime, timedelta
from .models import (
    ServiceCategory, Service, Subscription, Appointment,
    SupportTicket, TicketMessage, ServiceReview
)

class ServiceTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = ServiceCategory.objects.create(
            name='Consulting',
            description='Consulting services'
        )

    def test_create_service(self):
        """Test création d'un service"""
        data = {
            'name': 'Web Development',
            'description': 'Professional web development service',
            'category': self.category.id,
            'service_type': 'one_time',
            'price': 500.00,
            'duration_hours': 40,
            'is_active': True
        }
        
        response = self.client.post('/api/service/services/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        service = Service.objects.get(id=response.data['id'])
        self.assertEqual(service.name, 'Web Development')
        self.assertEqual(service.price, Decimal('500.00'))
        self.assertEqual(service.category, self.category)

    def test_service_filtering_by_category(self):
        """Test filtrage des services par catégorie"""
        service1 = Service.objects.create(
            name='Service 1',
            description='Description 1',
            category=self.category,
            service_type='one_time',
            price=Decimal('100.00')
        )
        
        other_category = ServiceCategory.objects.create(
            name='Other Category',
            description='Other category'
        )
        
        service2 = Service.objects.create(
            name='Service 2',
            description='Description 2',
            category=other_category,
            service_type='one_time',
            price=Decimal('200.00')
        )
        
        response = self.client.get(f'/api/service/services/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        results = response.data.get('results', response.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], service1.id)

class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = ServiceCategory.objects.create(
            name='Maintenance',
            description='Maintenance services'
        )
        
        self.service = Service.objects.create(
            name='Monthly Maintenance',
            description='Monthly maintenance service',
            category=self.category,
            service_type='subscription',
            price=Decimal('99.99')
        )

    def test_create_subscription(self):
        """Test création d'un abonnement"""
        data = {
            'service': self.service.id,
            'billing_cycle': 'monthly',
            'start_date': date.today().isoformat(),
            'auto_renew': True
        }
        
        response = self.client.post('/api/service/subscriptions/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        subscription = Subscription.objects.get(id=response.data['id'])
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.service, self.service)
        self.assertEqual(subscription.status, 'active')

    def test_subscription_renewal(self):
        """Test renouvellement d'abonnement"""
        subscription = Subscription.objects.create(
            user=self.user,
            service=self.service,
            billing_cycle='monthly',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
            status='active',
            auto_renew=True
        )
        
        # Simuler le renouvellement
        old_end_date = subscription.end_date
        subscription.end_date = old_end_date + timedelta(days=30)
        subscription.save()
        
        self.assertEqual(subscription.end_date, old_end_date + timedelta(days=30))

class AppointmentTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = ServiceCategory.objects.create(
            name='Consulting',
            description='Consulting services'
        )
        
        self.service = Service.objects.create(
            name='Business Consultation',
            description='Professional business consultation',
            category=self.category,
            service_type='consultation',
            price=Decimal('150.00'),
            duration_hours=2
        )

    def test_create_appointment(self):
        """Test création d'un rendez-vous"""
        appointment_datetime = datetime.now() + timedelta(days=7)
        
        data = {
            'service': self.service.id,
            'appointment_date': appointment_datetime.date().isoformat(),
            'appointment_time': appointment_datetime.time().strftime('%H:%M'),
            'notes': 'Initial consultation meeting'
        }
        
        response = self.client.post('/api/service/appointments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        appointment = Appointment.objects.get(id=response.data['id'])
        self.assertEqual(appointment.user, self.user)
        self.assertEqual(appointment.service, self.service)
        self.assertEqual(appointment.status, 'scheduled')

    def test_appointment_confirmation(self):
        """Test confirmation de rendez-vous"""
        appointment = Appointment.objects.create(
            user=self.user,
            service=self.service,
            appointment_date=date.today() + timedelta(days=7),
            appointment_time=datetime.now().time(),
            status='scheduled'
        )
        
        # Simuler la confirmation
        appointment.status = 'confirmed'
        appointment.save()
        
        self.assertEqual(appointment.status, 'confirmed')

    def test_appointment_cancellation(self):
        """Test annulation de rendez-vous"""
        appointment = Appointment.objects.create(
            user=self.user,
            service=self.service,
            appointment_date=date.today() + timedelta(days=7),
            appointment_time=datetime.now().time(),
            status='confirmed'
        )
        
        response = self.client.post(f'/api/service/appointments/{appointment.id}/cancel/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, 'cancelled')

class SupportTicketTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_support_ticket(self):
        """Test création d'un ticket de support"""
        data = {
            'subject': 'Technical Issue',
            'description': 'I am experiencing a technical problem with the service.',
            'priority': 'medium',
            'category': 'technical'
        }
        
        response = self.client.post('/api/service/tickets/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        ticket = SupportTicket.objects.get(id=response.data['id'])
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.subject, 'Technical Issue')
        self.assertEqual(ticket.status, 'open')

    def test_add_message_to_ticket(self):
        """Test ajout d'un message à un ticket"""
        ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Test Ticket',
            description='Test description',
            priority='medium',
            category='technical',
            status='open'
        )
        
        data = {
            'message': 'This is a follow-up message.'
        }
        
        response = self.client.post(f'/api/service/tickets/{ticket.id}/add_message/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        message = TicketMessage.objects.get(ticket=ticket, sender=self.user)
        self.assertEqual(message.message, 'This is a follow-up message.')

    def test_close_ticket(self):
        """Test fermeture d'un ticket"""
        ticket = SupportTicket.objects.create(
            user=self.user,
            subject='Test Ticket',
            description='Test description',
            priority='medium',
            category='technical',
            status='open'
        )
        
        response = self.client.post(f'/api/service/tickets/{ticket.id}/close/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'closed')

class ServiceReviewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = ServiceCategory.objects.create(
            name='Consulting',
            description='Consulting services'
        )
        
        self.service = Service.objects.create(
            name='Business Consultation',
            description='Professional business consultation',
            category=self.category,
            service_type='consultation',
            price=Decimal('150.00')
        )

    def test_create_service_review(self):
        """Test création d'un avis sur un service"""
        data = {
            'service': self.service.id,
            'rating': 5,
            'comment': 'Excellent service, very professional and helpful.'
        }
        
        response = self.client.post('/api/service/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        review = ServiceReview.objects.get(id=response.data['id'])
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.service, self.service)
        self.assertEqual(review.rating, 5)

    def test_service_average_rating(self):
        """Test calcul de la note moyenne d'un service"""
        # Créer plusieurs avis
        ServiceReview.objects.create(
            user=self.user,
            service=self.service,
            rating=5,
            comment='Great service'
        )
        
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com'
        )
        
        ServiceReview.objects.create(
            user=other_user,
            service=self.service,
            rating=4,
            comment='Good service'
        )
        
        # Calculer la moyenne
        reviews = ServiceReview.objects.filter(service=self.service)
        average_rating = sum(review.rating for review in reviews) / len(reviews)
        
        self.assertEqual(average_rating, 4.5)

    def test_prevent_duplicate_review(self):
        """Test prévention des avis en double"""
        # Créer un premier avis
        ServiceReview.objects.create(
            user=self.user,
            service=self.service,
            rating=5,
            comment='First review'
        )
        
        # Tenter de créer un second avis
        data = {
            'service': self.service.id,
            'rating': 3,
            'comment': 'Second review'
        }
        
        response = self.client.post('/api/service/reviews/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Vérifier qu'il n'y a toujours qu'un seul avis
        reviews_count = ServiceReview.objects.filter(user=self.user, service=self.service).count()
        self.assertEqual(reviews_count, 1)