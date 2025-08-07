from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from io import BytesIO
import os

def generate_invoice_pdf(invoice):
    """Génère un PDF pour une facture"""
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # En-tête
    p.setFont("Helvetica-Bold", 16)
    p.drawString(2*cm, height-2*cm, f"FACTURE {invoice.invoice_number}")
    
    # Informations entreprise
    p.setFont("Helvetica", 10)
    p.drawString(2*cm, height-3*cm, "Votre Entreprise")
    p.drawString(2*cm, height-3.5*cm, "123 Rue Example")
    p.drawString(2*cm, height-4*cm, "1000 Bruxelles")
    p.drawString(2*cm, height-4.5*cm, "TVA: BE0123456789")
    
    # Informations client
    if invoice.customer:
        p.drawString(12*cm, height-3*cm, f"Client: {invoice.customer.user.get_full_name()}")
        p.drawString(12*cm, height-3.5*cm, f"Email: {invoice.customer.user.email}")
        if invoice.customer.phone:
            p.drawString(12*cm, height-4*cm, f"Tél: {invoice.customer.phone}")
    
    # Dates
    p.drawString(2*cm, height-6*cm, f"Date facture: {invoice.invoice_date}")
    p.drawString(2*cm, height-6.5*cm, f"Date échéance: {invoice.due_date}")
    
    # Tableau des lignes
    y_position = height - 8*cm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(2*cm, y_position, "Description")
    p.drawString(10*cm, y_position, "Qté")
    p.drawString(12*cm, y_position, "Prix HT")
    p.drawString(14*cm, y_position, "TVA")
    p.drawString(16*cm, y_position, "Total HT")
    
    # Ligne de séparation
    p.line(2*cm, y_position-0.3*cm, 18*cm, y_position-0.3*cm)
    
    y_position -= 0.8*cm
    p.setFont("Helvetica", 9)
    
    # Lignes de facture
    for line in invoice.lines.all():
        p.drawString(2*cm, y_position, line.description[:40])
        p.drawString(10*cm, y_position, str(line.quantity))
        p.drawString(12*cm, y_position, f"€{line.unit_price_excl_vat}")
        p.drawString(14*cm, y_position, f"{line.vat_rate}%")
        p.drawString(16*cm, y_position, f"€{line.total_excl_vat}")
        y_position -= 0.5*cm
    
    # Totaux
    y_position -= 1*cm
    p.setFont("Helvetica-Bold", 10)
    p.drawString(14*cm, y_position, f"Total HT: €{invoice.subtotal_excl_vat}")
    y_position -= 0.5*cm
    p.drawString(14*cm, y_position, f"TVA: €{invoice.vat_amount}")
    y_position -= 0.5*cm
    p.drawString(14*cm, y_position, f"Total TTC: €{invoice.total_incl_vat}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer

def send_invoice_email(invoice):
    """Envoie la facture par email au client"""
    if not invoice.customer or not invoice.customer.user.email:
        return False, "Aucun email client trouvé"
    
    # Génération du PDF
    pdf_buffer = generate_invoice_pdf(invoice)
    
    # Préparation de l'email
    subject = f"Facture {invoice.invoice_number}"
    message = f"""
    Bonjour {invoice.customer.user.get_full_name()},
    
    Veuillez trouver ci-joint votre facture {invoice.invoice_number}.
    
    Montant: €{invoice.total_incl_vat}
    Date d'échéance: {invoice.due_date}
    
    Cordialement,
    Votre équipe
    """
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[invoice.customer.user.email]
    )
    
    # Attachement du PDF
    email.attach(
        f"facture_{invoice.invoice_number}.pdf",
        pdf_buffer.getvalue(),
        'application/pdf'
    )
    
    try:
        email.send()
        return True, "Email envoyé avec succès"
    except Exception as e:
        return False, f"Erreur envoi email: {str(e)}"

def get_invoices_by_period(year=None, quarter=None):
    """Récupère les factures par période"""
    from .models import Invoice
    
    queryset = Invoice.objects.all()
    
    if year:
        queryset = queryset.filter(invoice_date__year=year)
    
    if quarter:
        quarter_months = {
            1: [1, 2, 3],
            2: [4, 5, 6], 
            3: [7, 8, 9],
            4: [10, 11, 12]
        }
        if quarter in quarter_months:
            queryset = queryset.filter(invoice_date__month__in=quarter_months[quarter])
    
    return queryset.order_by('-invoice_date')