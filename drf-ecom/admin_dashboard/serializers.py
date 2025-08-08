from rest_framework import serializers
from .models import (
    Department, Employee, Leave,
    BelgianChartOfAccounts, AccountingJournal, AccountingEntry, AccountingEntryLine,
    BelgianVATDeclaration, Invoice, InvoiceLine, Payment
)

# ============ RESSOURCES HUMAINES ============

class DepartmentSerializer(serializers.ModelSerializer):
    manager_name = serializers.CharField(source='manager.get_full_name', read_only=True)
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Department
        fields = '__all__'

    def get_employees_count(self, obj):
        return obj.employee_set.filter(is_active=True).count()

class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Employee
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = Leave
        fields = '__all__'

# ============ COMPTABILITÉ ============

class BelgianChartOfAccountsSerializer(serializers.ModelSerializer):
    parent_account_name = serializers.CharField(source='parent_account.account_name', read_only=True)

    class Meta:
        model = BelgianChartOfAccounts
        fields = '__all__'

class AccountingJournalSerializer(serializers.ModelSerializer):
    entries_count = serializers.SerializerMethodField()

    class Meta:
        model = AccountingJournal
        fields = '__all__'

    def get_entries_count(self, obj):
        return obj.accountingentry_set.count()

class AccountingEntryLineSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.account_name', read_only=True)
    account_number = serializers.CharField(source='account.account_number', read_only=True)

    class Meta:
        model = AccountingEntryLine
        fields = '__all__'

class AccountingEntrySerializer(serializers.ModelSerializer):
    lines = AccountingEntryLineSerializer(many=True, read_only=True)
    journal_name = serializers.CharField(source='journal.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = AccountingEntry
        fields = '__all__'

class AccountingEntryCreateSerializer(serializers.ModelSerializer):
    lines = AccountingEntryLineSerializer(many=True)

    class Meta:
        model = AccountingEntry
        fields = ['journal', 'entry_date', 'description', 'reference', 'lines']

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        entry = AccountingEntry.objects.create(**validated_data)
        
        total_debit = 0
        total_credit = 0
        
        for line_data in lines_data:
            AccountingEntryLine.objects.create(entry=entry, **line_data)
            total_debit += line_data.get('debit_amount', 0)
            total_credit += line_data.get('credit_amount', 0)
        
        entry.total_debit = total_debit
        entry.total_credit = total_credit
        entry.save()
        
        return entry

class BelgianVATDeclarationSerializer(serializers.ModelSerializer):
    period_display = serializers.SerializerMethodField()

    class Meta:
        model = BelgianVATDeclaration
        fields = '__all__'

    def get_period_display(self, obj):
        if obj.period_type == 'monthly':
            return f"{obj.year}-{obj.period:02d}"
        else:
            return f"{obj.year}-T{obj.period}"

# ============ FACTURATION ============

class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        exclude = ['invoice']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)
    balance_due = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = '__all__'

    def get_balance_due(self, obj):
        total_payments = sum(payment.amount for payment in obj.payments.all())
        return obj.total_incl_vat - total_payments

class InvoiceCreateSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True)

    class Meta:
        model = Invoice
        fields = [
            'invoice_type', 'customer', 'supplier_name', 'invoice_date', 
            'due_date', 'billing_address', 'subtotal_excl_vat', 'vat_amount', 
            'total_incl_vat', 'order', 'notes', 'lines'
        ]

    def create(self, validated_data):
        lines_data = validated_data.pop('lines')
        invoice = Invoice.objects.create(**validated_data)
        
        for line_data in lines_data:
            InvoiceLine.objects.create(invoice=invoice, **line_data)
        
        return invoice