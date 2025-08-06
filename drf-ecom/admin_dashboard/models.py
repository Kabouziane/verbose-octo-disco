from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from shop.models import Customer, Order

# ============ RESSOURCES HUMAINES ============

class Department(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    EMPLOYMENT_TYPES = [
        ('full_time', 'Temps plein'),
        ('part_time', 'Temps partiel'),
        ('contractor', 'Contractuel'),
        ('intern', 'Stagiaire'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    hire_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    national_number = models.CharField(max_length=11, unique=True)  # Numéro national belge

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class Leave(models.Model):
    LEAVE_TYPES = [
        ('vacation', 'Congés payés'),
        ('sick', 'Congé maladie'),
        ('maternity', 'Congé maternité'),
        ('paternity', 'Congé paternité'),
        ('unpaid', 'Congé sans solde'),
    ]

    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Refusé'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_count = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

# ============ COMPTABILITÉ BELGE ============

class BelgianChartOfAccounts(models.Model):
    """Plan comptable belge basé sur le PCMN (Plan Comptable Minimum Normalisé)"""
    
    ACCOUNT_TYPES = [
        ('1', 'Fonds propres, provisions et dettes à plus d\'un an'),
        ('2', 'Frais d\'établissement, actifs immobilisés et créances à plus d\'un an'),
        ('3', 'Stock et commandes en cours d\'exécution'),
        ('4', 'Créances et dettes à un an au plus'),
        ('5', 'Placements de trésorerie et valeurs disponibles'),
        ('6', 'Charges'),
        ('7', 'Produits'),
    ]

    account_number = models.CharField(max_length=10, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=1, choices=ACCOUNT_TYPES)
    parent_account = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['account_number']

    def __str__(self):
        return f"{self.account_number} - {self.account_name}"

class AccountingJournal(models.Model):
    """Journaux comptables belges"""
    
    JOURNAL_TYPES = [
        ('sales', 'Journal des ventes'),
        ('purchases', 'Journal des achats'),
        ('cash', 'Journal de caisse'),
        ('bank', 'Journal de banque'),
        ('general', 'Journal général'),
        ('opening', 'Journal d\'ouverture'),
        ('closing', 'Journal de clôture'),
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    journal_type = models.CharField(max_length=20, choices=JOURNAL_TYPES)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.name}"

class AccountingEntry(models.Model):
    """Écriture comptable"""
    
    journal = models.ForeignKey(AccountingJournal, on_delete=models.CASCADE)
    entry_number = models.CharField(max_length=20)
    entry_date = models.DateField()
    description = models.CharField(max_length=200)
    reference = models.CharField(max_length=50, blank=True)
    total_debit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_credit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    is_balanced = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['journal', 'entry_number']

    def __str__(self):
        return f"{self.journal.code}-{self.entry_number} - {self.description}"

    def save(self, *args, **kwargs):
        # Vérifier l'équilibre débit/crédit
        self.is_balanced = self.total_debit == self.total_credit
        super().save(*args, **kwargs)

class AccountingEntryLine(models.Model):
    """Ligne d'écriture comptable"""
    
    entry = models.ForeignKey(AccountingEntry, related_name='lines', on_delete=models.CASCADE)
    account = models.ForeignKey(BelgianChartOfAccounts, on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vat_code = models.CharField(max_length=10, blank=True)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.account.account_number} - {self.description}"

class BelgianVATDeclaration(models.Model):
    """Déclaration TVA belge périodique"""
    
    PERIODS = [
        ('monthly', 'Mensuelle'),
        ('quarterly', 'Trimestrielle'),
    ]

    period_type = models.CharField(max_length=20, choices=PERIODS)
    year = models.PositiveIntegerField()
    period = models.PositiveIntegerField()  # Mois (1-12) ou trimestre (1-4)
    
    # Grilles TVA belges principales
    grid_00_operations_exempted = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_01_operations_6_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_02_operations_12_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_03_operations_21_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # TVA due
    grid_54_vat_6_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_55_vat_12_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_56_vat_21_percent = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # TVA déductible
    grid_59_vat_deductible = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Solde
    grid_71_vat_to_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    grid_72_vat_to_recover = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    is_submitted = models.BooleanField(default=False)
    submission_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['period_type', 'year', 'period']

# ============ FACTURATION ============

class Invoice(models.Model):
    INVOICE_TYPES = [
        ('sale', 'Facture de vente'),
        ('purchase', 'Facture d\'achat'),
        ('credit_note', 'Note de crédit'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('sent', 'Envoyée'),
        ('paid', 'Payée'),
        ('overdue', 'En retard'),
        ('cancelled', 'Annulée'),
    ]

    invoice_number = models.CharField(max_length=20, unique=True)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPES)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    supplier_name = models.CharField(max_length=200, blank=True)  # Pour factures d'achat
    invoice_date = models.DateField()
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Montants
    subtotal_excl_vat = models.DecimalField(max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_incl_vat = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Adresses
    billing_address = models.JSONField()
    
    # Références
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    accounting_entry = models.ForeignKey(AccountingEntry, on_delete=models.SET_NULL, null=True, blank=True)
    
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Facture {self.invoice_number}"

class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name='lines', on_delete=models.CASCADE)
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price_excl_vat = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=4, decimal_places=2)
    total_excl_vat = models.DecimalField(max_digits=15, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=15, decimal_places=2)
    total_incl_vat = models.DecimalField(max_digits=15, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total_excl_vat = self.quantity * self.unit_price_excl_vat
        self.vat_amount = self.total_excl_vat * (self.vat_rate / 100)
        self.total_incl_vat = self.total_excl_vat + self.vat_amount
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Espèces'),
        ('bank_transfer', 'Virement bancaire'),
        ('card', 'Carte bancaire'),
        ('check', 'Chèque'),
        ('stripe', 'Stripe'),
    ]

    invoice = models.ForeignKey(Invoice, related_name='payments', on_delete=models.CASCADE)
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Paiement {self.amount}€ - {self.invoice.invoice_number}"