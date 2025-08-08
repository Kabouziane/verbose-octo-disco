from django.core.management.base import BaseCommand
from admin_dashboard.models import BelgianChartOfAccounts, AccountingJournal

class Command(BaseCommand):
    help = 'Initialise le plan comptable belge (PCMN) et les journaux'

    def handle(self, *args, **options):
        self.stdout.write('🏦 Initialisation du plan comptable belge...')
        
        # Plan comptable de base
        accounts = [
            # Classe 1 - Fonds propres
            ('100000', 'Capital', '1'),
            ('140000', 'Bénéfice reporté', '1'),
            ('170000', 'Dettes à plus d\'un an', '1'),
            
            # Classe 2 - Actifs immobilisés
            ('200000', 'Frais d\'établissement', '2'),
            ('220000', 'Terrains et constructions', '2'),
            ('240000', 'Installations, machines et outillage', '2'),
            ('280000', 'Amortissements', '2'),
            
            # Classe 3 - Stocks
            ('300000', 'Approvisionnements', '3'),
            ('320000', 'En-cours de fabrication', '3'),
            ('340000', 'Produits finis', '3'),
            ('370000', 'Commandes en cours d\'exécution', '3'),
            
            # Classe 4 - Créances et dettes
            ('400000', 'Fournisseurs', '4'),
            ('410000', 'Clients', '4'),
            ('411000', 'Effets à recevoir', '4'),
            ('450000', 'Dettes fiscales et sociales', '4'),
            ('451000', 'TVA à payer', '4'),
            ('452000', 'TVA déductible', '4'),
            ('454000', 'ONSS', '4'),
            ('455000', 'Précompte professionnel', '4'),
            
            # Classe 5 - Trésorerie
            ('500000', 'Actions et parts', '5'),
            ('550000', 'Banques', '5'),
            ('570000', 'Caisse', '5'),
            
            # Classe 6 - Charges
            ('600000', 'Achats de marchandises', '6'),
            ('610000', 'Services et biens divers', '6'),
            ('620000', 'Rémunérations et charges sociales', '6'),
            ('630000', 'Amortissements', '6'),
            ('640000', 'Autres charges d\'exploitation', '6'),
            ('650000', 'Charges financières', '6'),
            ('670000', 'Charges exceptionnelles', '6'),
            ('690000', 'Impôts sur le résultat', '6'),
            
            # Classe 7 - Produits
            ('700000', 'Chiffre d\'affaires', '7'),
            ('740000', 'Autres produits d\'exploitation', '7'),
            ('750000', 'Produits financiers', '7'),
            ('770000', 'Produits exceptionnels', '7'),
        ]
        
        created_accounts = 0
        for account_number, account_name, account_type in accounts:
            account, created = BelgianChartOfAccounts.objects.get_or_create(
                account_number=account_number,
                defaults={
                    'account_name': account_name,
                    'account_type': account_type,
                    'is_active': True
                }
            )
            if created:
                created_accounts += 1
        
        self.stdout.write(f'✅ {created_accounts} comptes créés')
        
        # Journaux comptables
        journals = [
            ('VTE', 'Journal des ventes', 'sales'),
            ('ACH', 'Journal des achats', 'purchases'),
            ('CAI', 'Journal de caisse', 'cash'),
            ('BNQ', 'Journal de banque', 'bank'),
            ('OD', 'Opérations diverses', 'general'),
        ]
        
        created_journals = 0
        for code, name, journal_type in journals:
            journal, created = AccountingJournal.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'journal_type': journal_type,
                    'is_active': True
                }
            )
            if created:
                created_journals += 1
        
        self.stdout.write(f'✅ {created_journals} journaux créés')
        self.stdout.write('🎉 Plan comptable belge initialisé avec succès !')