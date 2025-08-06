from django.core.management.base import BaseCommand
from admin_dashboard.models import BelgianChartOfAccounts, AccountingJournal

class Command(BaseCommand):
    help = 'Initialise le plan comptable belge (PCMN) et les journaux'

    def handle(self, *args, **options):
        self.stdout.write('Création du plan comptable belge...')
        
        # Plan comptable belge simplifié basé sur le PCMN
        accounts = [
            # Classe 1 - Fonds propres, provisions et dettes à plus d'un an
            ('10', 'Capital', '1'),
            ('100', 'Capital souscrit', '1'),
            ('101', 'Capital non appelé', '1'),
            ('12', 'Plus-values de réévaluation', '1'),
            ('13', 'Réserves', '1'),
            ('130', 'Réserves légales', '1'),
            ('131', 'Réserves indisponibles', '1'),
            ('14', 'Bénéfice reporté', '1'),
            ('15', 'Subsides en capital', '1'),
            ('16', 'Provisions et impôts différés', '1'),
            ('17', 'Dettes à plus d\'un an', '1'),
            ('170', 'Emprunts subordonnés', '1'),
            ('171', 'Emprunts obligataires non convertibles', '1'),
            ('172', 'Emprunts obligataires convertibles', '1'),
            ('173', 'Emprunts et dettes de location-financement', '1'),
            ('174', 'Autres emprunts', '1'),
            
            # Classe 2 - Frais d'établissement, actifs immobilisés
            ('20', 'Frais d\'établissement', '2'),
            ('21', 'Immobilisations incorporelles', '2'),
            ('22', 'Terrains et constructions', '2'),
            ('220', 'Terrains', '2'),
            ('221', 'Constructions', '2'),
            ('23', 'Installations, machines et outillage', '2'),
            ('24', 'Mobilier et matériel roulant', '2'),
            ('240', 'Mobilier', '2'),
            ('241', 'Matériel roulant', '2'),
            ('25', 'Immobilisations détenues en location-financement', '2'),
            ('26', 'Autres immobilisations corporelles', '2'),
            ('27', 'Immobilisations financières', '2'),
            ('28', 'Amortissements des immobilisations', '2'),
            
            # Classe 3 - Stock et commandes en cours
            ('30', 'Approvisionnements - matières premières', '3'),
            ('31', 'Approvisionnements - fournitures', '3'),
            ('32', 'En-cours de fabrication', '3'),
            ('33', 'Produits finis', '3'),
            ('34', 'Marchandises', '3'),
            ('35', 'Immeubles destinés à la vente', '3'),
            ('36', 'Acomptes versés sur achats', '3'),
            ('37', 'Commandes en cours d\'exécution', '3'),
            
            # Classe 4 - Créances et dettes à un an au plus
            ('40', 'Créances commerciales', '4'),
            ('400', 'Clients', '4'),
            ('401', 'Effets à recevoir', '4'),
            ('402', 'Clients, créances douteuses', '4'),
            ('41', 'Autres créances', '4'),
            ('411', 'TVA à récupérer', '4'),
            ('412', 'Impôts et versements fiscaux à récupérer', '4'),
            ('44', 'Dettes commerciales', '4'),
            ('440', 'Fournisseurs', '4'),
            ('441', 'Effets à payer', '4'),
            ('45', 'Dettes fiscales, salariales et sociales', '4'),
            ('450', 'Dettes fiscales estimées', '4'),
            ('451', 'TVA à payer', '4'),
            ('452', 'Impôts et taxes à payer', '4'),
            ('453', 'Précomptes retenus', '4'),
            ('454', 'ONSS', '4'),
            ('455', 'Rémunérations', '4'),
            ('47', 'Dettes diverses', '4'),
            ('48', 'Comptes de régularisation', '4'),
            
            # Classe 5 - Placements de trésorerie et valeurs disponibles
            ('50', 'Actions et parts', '5'),
            ('51', 'Créances à plus d\'un an échéant dans l\'année', '5'),
            ('52', 'Créances à court terme', '5'),
            ('53', 'Dépôts à terme', '5'),
            ('54', 'Valeurs échues à l\'encaissement', '5'),
            ('55', 'Établissements de crédit', '5'),
            ('550', 'Comptes courants bancaires', '5'),
            ('56', 'Office des chèques postaux', '5'),
            ('57', 'Caisses', '5'),
            ('570', 'Caisse espèces', '5'),
            ('58', 'Virements internes', '5'),
            
            # Classe 6 - Charges
            ('60', 'Approvisionnements et marchandises', '6'),
            ('600', 'Achats de matières premières', '6'),
            ('601', 'Achats de fournitures', '6'),
            ('602', 'Achats de services, travaux et études', '6'),
            ('603', 'Sous-traitances générales', '6'),
            ('604', 'Achats de marchandises', '6'),
            ('61', 'Services et biens divers', '6'),
            ('610', 'Loyers et charges locatives', '6'),
            ('611', 'Entretien et réparation', '6'),
            ('612', 'Fournitures faites à l\'entreprise', '6'),
            ('613', 'Rétributions de tiers', '6'),
            ('614', 'Annonces, publicité', '6'),
            ('615', 'Sous-traitances générales', '6'),
            ('616', 'Primes d\'assurances', '6'),
            ('617', 'Commissions aux tiers', '6'),
            ('618', 'Rémunérations, prix, commissions et courtages', '6'),
            ('62', 'Rémunérations, charges sociales et pensions', '6'),
            ('620', 'Rémunérations et avantages sociaux directs', '6'),
            ('621', 'Cotisations patronales de sécurité sociale', '6'),
            ('622', 'Primes patronales pour assurances extralégales', '6'),
            ('623', 'Autres frais de personnel', '6'),
            ('624', 'Pensions', '6'),
            ('63', 'Amortissements, réductions de valeur et provisions', '6'),
            ('630', 'Dotations aux amortissements', '6'),
            ('631', 'Réductions de valeur sur stocks', '6'),
            ('632', 'Réductions de valeur sur créances commerciales', '6'),
            ('64', 'Autres charges d\'exploitation', '6'),
            ('640', 'Charges fiscales d\'exploitation', '6'),
            ('641', 'Moins-values sur réalisations d\'immobilisations', '6'),
            ('65', 'Charges financières', '6'),
            ('650', 'Charges des dettes', '6'),
            ('651', 'Réductions de valeur sur actifs circulants', '6'),
            ('66', 'Charges exceptionnelles', '6'),
            ('67', 'Impôts sur le résultat', '6'),
            ('670', 'Impôts belges sur le résultat', '6'),
            
            # Classe 7 - Produits
            ('70', 'Chiffre d\'affaires', '7'),
            ('700', 'Ventes de marchandises', '7'),
            ('701', 'Ventes de produits finis', '7'),
            ('702', 'Ventes de déchets et rebuts', '7'),
            ('703', 'Ventes d\'emballages récupérables', '7'),
            ('704', 'Facturations des travaux en cours', '7'),
            ('705', 'Prestations de services', '7'),
            ('71', 'Variation des stocks et des commandes en cours', '7'),
            ('72', 'Production immobilisée', '7'),
            ('74', 'Autres produits d\'exploitation', '7'),
            ('740', 'Subsides d\'exploitation et montants compensatoires', '7'),
            ('741', 'Plus-values sur réalisations d\'actifs immobilisés', '7'),
            ('75', 'Produits financiers', '7'),
            ('750', 'Produits des immobilisations financières', '7'),
            ('751', 'Produits des actifs circulants', '7'),
            ('752', 'Plus-values sur réalisations d\'actifs circulants', '7'),
            ('753', 'Subsides en capital et en intérêts', '7'),
            ('754', 'Différences de change', '7'),
            ('76', 'Produits exceptionnels', '7'),
        ]
        
        for account_number, account_name, account_type in accounts:
            BelgianChartOfAccounts.objects.get_or_create(
                account_number=account_number,
                defaults={
                    'account_name': account_name,
                    'account_type': account_type,
                    'is_active': True
                }
            )
        
        self.stdout.write('Création des journaux comptables...')
        
        # Journaux comptables belges
        journals = [
            ('VTE', 'Journal des ventes', 'sales'),
            ('ACH', 'Journal des achats', 'purchases'),
            ('CAI', 'Journal de caisse', 'cash'),
            ('BNQ', 'Journal de banque', 'bank'),
            ('OD', 'Opérations diverses', 'general'),
            ('OUV', 'Journal d\'ouverture', 'opening'),
            ('CLO', 'Journal de clôture', 'closing'),
        ]
        
        for code, name, journal_type in journals:
            AccountingJournal.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'journal_type': journal_type,
                    'is_active': True
                }
            )
        
        self.stdout.write(
            self.style.SUCCESS('Plan comptable belge et journaux créés avec succès!')
        )