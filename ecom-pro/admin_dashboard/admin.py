from django.contrib import admin
from .models import Department, Employee, BelgianChartOfAccounts, AccountingJournal, Invoice

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'manager']

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['user', 'employee_id', 'department', 'is_active']
    list_filter = ['department', 'is_active']

@admin.register(BelgianChartOfAccounts)
class BelgianChartOfAccountsAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'account_name', 'account_type']
    list_filter = ['account_type']
    ordering = ['account_number']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'invoice_date', 'status', 'total_incl_vat']
    list_filter = ['status', 'invoice_type']