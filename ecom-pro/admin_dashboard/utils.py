from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def generate_invoice_pdf(invoice):
    """Générer un PDF pour une facture"""
    try:
        # Pour l'instant, retourner un PDF simple
        buffer = BytesIO()
        buffer.write(b"PDF Invoice Content - To be implemented with reportlab")
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Error generating PDF for invoice {invoice.id}: {e}")
        raise

def send_invoice_email(invoice):
    """Envoyer une facture par email"""
    try:
        if not invoice.customer or not invoice.customer.user_email:
            return False, "Aucun email client disponible"
        
        subject = f"Facture {invoice.invoice_number}"
        message = f"""
        Bonjour,
        
        Veuillez trouver ci-joint votre facture {invoice.invoice_number}.
        
        Montant: €{invoice.total_incl_vat}
        Date d'échéance: {invoice.due_date}
        
        Cordialement,
        L'équipe
        """
        
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.customer.user_email]
        )
        
        # Ajouter le PDF en pièce jointe
        pdf_buffer = generate_invoice_pdf(invoice)
        email.attach(f"facture_{invoice.invoice_number}.pdf", pdf_buffer.getvalue(), 'application/pdf')
        
        email.send()
        return True, "Email envoyé avec succès"
        
    except Exception as e:
        logger.error(f"Error sending email for invoice {invoice.id}: {e}")
        return False, f"Erreur lors de l'envoi: {str(e)}"

def get_invoices_by_period(year=None, quarter=None):
    """Récupérer les factures par période"""
    from .models import Invoice
    
    queryset = Invoice.objects.all()
    
    if year:
        queryset = queryset.filter(invoice_date__year=year)
    
    if quarter:
        quarter_months = {
            '1': [1, 2, 3],
            '2': [4, 5, 6], 
            '3': [7, 8, 9],
            '4': [10, 11, 12]
        }
        if quarter in quarter_months:
            queryset = queryset.filter(invoice_date__month__in=quarter_months[quarter])
    
    return queryset.order_by('-invoice_date')