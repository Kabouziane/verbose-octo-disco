from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    Department, Employee, Leave,
    BelgianChartOfAccounts, AccountingJournal, AccountingEntry,
    BelgianVATDeclaration, Invoice, Payment
)
from .serializers import (
    DepartmentSerializer, EmployeeSerializer, LeaveSerializer,
    BelgianChartOfAccountsSerializer, AccountingJournalSerializer,
    AccountingEntrySerializer, AccountingEntryCreateSerializer,
    BelgianVATDeclarationSerializer, InvoiceSerializer, InvoiceCreateSerializer,
    PaymentSerializer
)

# ============ RESSOURCES HUMAINES ============

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['department', 'employment_type', 'is_active']
    search_fields = ['user__first_name', 'user__last_name', 'employee_id']

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        total_employees = Employee.objects.filter(is_active=True).count()
        by_department = Employee.objects.filter(is_active=True).values(
            'department__name'
        ).annotate(count=models.Count('id'))
        
        return Response({
            'total_employees': total_employees,
            'by_department': list(by_department)
        })

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.all()
    serializer_class = LeaveSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['employee', 'leave_type', 'status']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.approved_by = request.user
        leave.save()
        return Response({'status': 'approved'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'rejected'
        leave.approved_by = request.user
        leave.save()
        return Response({'status': 'rejected'})

# ============ COMPTABILITÉ ============

class BelgianChartOfAccountsViewSet(viewsets.ModelViewSet):
    queryset = BelgianChartOfAccounts.objects.filter(is_active=True)
    serializer_class = BelgianChartOfAccountsSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['account_type']
    search_fields = ['account_number', 'account_name']
    ordering = ['account_number']

class AccountingJournalViewSet(viewsets.ModelViewSet):
    queryset = AccountingJournal.objects.filter(is_active=True)
    serializer_class = AccountingJournalSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

class AccountingEntryViewSet(viewsets.ModelViewSet):
    queryset = AccountingEntry.objects.all()
    serializer_class = AccountingEntrySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['journal', 'entry_date']
    ordering = ['-entry_date', '-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return AccountingEntryCreateSerializer
        return AccountingEntrySerializer

    def perform_create(self, serializer):
        # Générer le numéro d'écriture automatiquement
        journal = serializer.validated_data['journal']
        last_entry = AccountingEntry.objects.filter(journal=journal).order_by('-entry_number').first()
        
        if last_entry:
            last_number = int(last_entry.entry_number.split('-')[-1])
            entry_number = f"{timezone.now().year}-{last_number + 1:06d}"
        else:
            entry_number = f"{timezone.now().year}-000001"
        
        serializer.save(
            entry_number=entry_number,
            created_by=self.request.user
        )

    @action(detail=False, methods=['get'])
    def trial_balance(self, request):
        """Balance de vérification"""
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        
        entries = AccountingEntry.objects.filter(is_balanced=True)
        if date_from:
            entries = entries.filter(entry_date__gte=date_from)
        if date_to:
            entries = entries.filter(entry_date__lte=date_to)
        
        # Calculer les soldes par compte
        accounts_balance = {}
        for entry in entries:
            for line in entry.lines.all():
                account_number = line.account.account_number
                if account_number not in accounts_balance:
                    accounts_balance[account_number] = {
                        'account_name': line.account.account_name,
                        'debit': Decimal('0'),
                        'credit': Decimal('0')
                    }
                
                accounts_balance[account_number]['debit'] += line.debit_amount
                accounts_balance[account_number]['credit'] += line.credit_amount
        
        return Response(accounts_balance)

class BelgianVATDeclarationViewSet(viewsets.ModelViewSet):
    queryset = BelgianVATDeclaration.objects.all()
    serializer_class = BelgianVATDeclarationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    ordering = ['-year', '-period']

    @action(detail=False, methods=['post'])
    def generate_declaration(self, request):
        """Générer automatiquement une déclaration TVA"""
        year = int(request.data.get('year'))
        period = int(request.data.get('period'))
        period_type = request.data.get('period_type', 'monthly')
        
        # Calculer les dates de début et fin de période
        if period_type == 'monthly':
            start_date = datetime(year, period, 1).date()
            if period == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, period + 1, 1).date() - timedelta(days=1)
        else:  # quarterly
            start_month = (period - 1) * 3 + 1
            start_date = datetime(year, start_month, 1).date()
            end_month = start_month + 2
            if end_month > 12:
                end_date = datetime(year + 1, end_month - 12, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, end_month + 1, 1).date() - timedelta(days=1)
        
        # Récupérer les factures de la période
        invoices = Invoice.objects.filter(
            invoice_type='sale',
            invoice_date__gte=start_date,
            invoice_date__lte=end_date,
            status__in=['sent', 'paid']
        )
        
        # Calculer les montants par taux de TVA
        operations_21 = invoices.filter(
            lines__vat_rate=21
        ).aggregate(total=Sum('lines__total_excl_vat'))['total'] or Decimal('0')
        
        operations_6 = invoices.filter(
            lines__vat_rate=6
        ).aggregate(total=Sum('lines__total_excl_vat'))['total'] or Decimal('0')
        
        operations_0 = invoices.filter(
            lines__vat_rate=0
        ).aggregate(total=Sum('lines__total_excl_vat'))['total'] or Decimal('0')
        
        # Calculer la TVA due
        vat_21 = operations_21 * Decimal('0.21')
        vat_6 = operations_6 * Decimal('0.06')
        
        # Créer la déclaration
        declaration = BelgianVATDeclaration.objects.create(
            period_type=period_type,
            year=year,
            period=period,
            grid_00_operations_exempted=operations_0,
            grid_01_operations_6_percent=operations_6,
            grid_03_operations_21_percent=operations_21,
            grid_55_vat_12_percent=vat_6,
            grid_56_vat_21_percent=vat_21,
            grid_71_vat_to_pay=vat_21 + vat_6
        )
        
        serializer = self.get_serializer(declaration)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# ============ FACTURATION ============

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['invoice_type', 'status', 'customer']
    search_fields = ['invoice_number', 'customer__user__email']
    ordering = ['-invoice_date']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        return InvoiceSerializer

    def perform_create(self, serializer):
        # Générer le numéro de facture automatiquement
        year = timezone.now().year
        last_invoice = Invoice.objects.filter(
            invoice_number__startswith=f"FAC{year}"
        ).order_by('-invoice_number').first()
        
        if last_invoice:
            last_number = int(last_invoice.invoice_number[-4:])
            invoice_number = f"FAC{year}{last_number + 1:04d}"
        else:
            invoice_number = f"FAC{year}0001"
        
        serializer.save(invoice_number=invoice_number)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        invoice = self.get_object()
        invoice.status = 'paid'
        invoice.save()
        return Response({'status': 'marked_as_paid'})

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Factures en retard"""
        overdue_invoices = Invoice.objects.filter(
            due_date__lt=timezone.now().date(),
            status__in=['sent']
        )
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    filterset_fields = ['invoice', 'payment_method']
    ordering = ['-payment_date']