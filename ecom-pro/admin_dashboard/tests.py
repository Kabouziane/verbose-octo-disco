from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta
from shop.models import Customer
from .models import (
    Department, Employee, Leave, Invoice, InvoiceLine, Payment,
    BelgianChartOfAccounts, AccountingJournal, AccountingEntry,
    BelgianVATDeclaration
)

class InvoiceTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            is_business=True,
            company_name='Test Company',
            vat_number='BE0123456789',
            user_email='test@example.com'
        )

    def test_create_invoice(self):
        """Test création d'une facture"""
        data = {
            'invoice_type': 'sale',
            'customer': self.customer.id,
            'invoice_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=30)).isoformat(),
            'billing_address': 'Test Address',
            'subtotal_excl_vat': 100.00,
            'vat_amount': 21.00,
            'total_incl_vat': 121.00,
            'lines': [
                {
                    'description': 'Test Product',
                    'quantity': 1,
                    'unit_price_excl_vat': 100.00,
                    'vat_rate': 21,
                    'total_excl_vat': 100.00,
                    'vat_amount': 21.00,
                    'total_incl_vat': 121.00
                }
            ]
        }
        
        response = self.client.post('/api/admin-dashboard/invoices/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        invoice = Invoice.objects.get(id=response.data['id'])
        self.assertEqual(invoice.customer, self.customer)
        self.assertEqual(invoice.subtotal_excl_vat, Decimal('100.00'))
        self.assertEqual(invoice.lines.count(), 1)

    def test_invoice_calculations(self):
        """Test calculs automatiques des lignes de facture"""
        invoice = Invoice.objects.create(
            invoice_type='sale',
            customer=self.customer,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            billing_address='Test Address',
            subtotal_excl_vat=Decimal('100.00'),
            vat_amount=Decimal('21.00'),
            total_incl_vat=Decimal('121.00')
        )
        
        line = InvoiceLine.objects.create(
            invoice=invoice,
            description='Test Product',
            quantity=2,
            unit_price_excl_vat=Decimal('50.00'),
            vat_rate=Decimal('21.00')
        )
        
        self.assertEqual(line.total_excl_vat, Decimal('100.00'))
        self.assertEqual(line.vat_amount, Decimal('21.00'))
        self.assertEqual(line.total_incl_vat, Decimal('121.00'))

    def test_invoice_number_generation(self):
        """Test génération automatique du numéro de facture"""
        data = {
            'invoice_type': 'sale',
            'customer': self.customer.id,
            'invoice_date': date.today().isoformat(),
            'due_date': (date.today() + timedelta(days=30)).isoformat(),
            'billing_address': 'Test Address',
            'subtotal_excl_vat': 100.00,
            'vat_amount': 21.00,
            'total_incl_vat': 121.00,
            'lines': []
        }
        
        response = self.client.post('/api/admin-dashboard/invoices/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        invoice = Invoice.objects.get(id=response.data['id'])
        self.assertTrue(invoice.invoice_number.startswith('FAC2024'))

class EmployeeTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.department = Department.objects.create(
            name='IT Department',
            description='Information Technology'
        )
        
        self.employee_user = User.objects.create_user(
            username='employee',
            email='employee@example.com',
            first_name='John',
            last_name='Doe'
        )

    def test_create_employee(self):
        """Test création d'un employé"""
        data = {
            'user': self.employee_user.id,
            'employee_id': 'EMP001',
            'department': self.department.id,
            'position': 'Developer',
            'employment_type': 'full_time',
            'hire_date': date.today().isoformat(),
            'salary': 50000.00,
            'national_number': '12345678901'
        }
        
        response = self.client.post('/api/admin-dashboard/employees/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        employee = Employee.objects.get(id=response.data['id'])
        self.assertEqual(employee.employee_id, 'EMP001')
        self.assertEqual(employee.department, self.department)

    def test_leave_request(self):
        """Test demande de congé"""
        employee = Employee.objects.create(
            user=self.employee_user,
            employee_id='EMP001',
            department=self.department,
            position='Developer',
            employment_type='full_time',
            hire_date=date.today(),
            salary=Decimal('50000.00'),
            national_number='12345678901'
        )
        
        data = {
            'employee': employee.id,
            'leave_type': 'vacation',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=5)).isoformat(),
            'days_count': 5,
            'reason': 'Family vacation'
        }
        
        response = self.client.post('/api/admin-dashboard/leaves/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        leave = Leave.objects.get(id=response.data['id'])
        self.assertEqual(leave.status, 'pending')

class AccountingTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.account = BelgianChartOfAccounts.objects.create(
            account_number='400000',
            account_name='Fournisseurs',
            account_type='4'
        )
        
        self.journal = AccountingJournal.objects.create(
            code='ACH',
            name='Journal des achats',
            journal_type='purchases'
        )

    def test_create_accounting_entry(self):
        """Test création d'une écriture comptable"""
        data = {
            'journal': self.journal.id,
            'entry_date': date.today().isoformat(),
            'description': 'Test entry',
            'lines': [
                {
                    'account': self.account.id,
                    'description': 'Test line',
                    'debit_amount': 100.00,
                    'credit_amount': 0.00
                }
            ]
        }
        
        response = self.client.post('/api/admin-dashboard/accounting-entries/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        entry = AccountingEntry.objects.get(id=response.data['id'])
        self.assertEqual(entry.lines.count(), 1)
        self.assertTrue(entry.entry_number.startswith('2024-'))

class VATDeclarationTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        # Créer des factures de test
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            is_business=True,
            company_name='Customer Company',
            user_email='customer@example.com'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='FAC20240001',
            invoice_type='sale',
            customer=self.customer,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            status='paid',
            billing_address='Customer Address',
            subtotal_excl_vat=Decimal('1000.00'),
            vat_amount=Decimal('210.00'),
            total_incl_vat=Decimal('1210.00')
        )
        
        InvoiceLine.objects.create(
            invoice=self.invoice,
            description='Test Product',
            quantity=1,
            unit_price_excl_vat=Decimal('1000.00'),
            vat_rate=Decimal('21.00'),
            total_excl_vat=Decimal('1000.00'),
            vat_amount=Decimal('210.00'),
            total_incl_vat=Decimal('1210.00')
        )

    def test_generate_vat_declaration(self):
        """Test génération d'une déclaration TVA"""
        data = {
            'year': 2024,
            'period': 1,
            'period_type': 'monthly'
        }
        
        response = self.client.post('/api/admin-dashboard/vat-declarations/generate_declaration/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        declaration = BelgianVATDeclaration.objects.get(id=response.data['id'])
        self.assertEqual(declaration.year, 2024)
        self.assertEqual(declaration.period, 1)

class PaymentTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.client.force_authenticate(user=self.admin_user)
        
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            is_business=True,
            company_name='Customer Company',
            user_email='customer@example.com'
        )
        
        self.invoice = Invoice.objects.create(
            invoice_number='FAC20240001',
            invoice_type='sale',
            customer=self.customer,
            invoice_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            billing_address='Customer Address',
            subtotal_excl_vat=Decimal('1000.00'),
            vat_amount=Decimal('210.00'),
            total_incl_vat=Decimal('1210.00')
        )

    def test_create_payment(self):
        """Test création d'un paiement"""
        data = {
            'invoice': self.invoice.id,
            'payment_date': date.today().isoformat(),
            'amount': 1210.00,
            'payment_method': 'bank_transfer',
            'reference': 'TRANSFER123'
        }
        
        response = self.client.post('/api/admin-dashboard/payments/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        payment = Payment.objects.get(id=response.data['id'])
        self.assertEqual(payment.amount, Decimal('1210.00'))
        self.assertEqual(payment.invoice, self.invoice)

    def test_mark_invoice_as_paid(self):
        """Test marquer une facture comme payée"""
        response = self.client.post(f'/api/admin-dashboard/invoices/{self.invoice.id}/mark_as_paid/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.status, 'paid')