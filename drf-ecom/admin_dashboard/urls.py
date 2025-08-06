from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DepartmentViewSet, EmployeeViewSet, LeaveViewSet,
    BelgianChartOfAccountsViewSet, AccountingJournalViewSet, AccountingEntryViewSet,
    BelgianVATDeclarationViewSet, InvoiceViewSet, PaymentViewSet
)

router = DefaultRouter()

# Ressources Humaines
router.register(r'departments', DepartmentViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'leaves', LeaveViewSet)

# Comptabilité
router.register(r'chart-of-accounts', BelgianChartOfAccountsViewSet)
router.register(r'journals', AccountingJournalViewSet)
router.register(r'entries', AccountingEntryViewSet)
router.register(r'vat-declarations', BelgianVATDeclarationViewSet)

# Facturation
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]