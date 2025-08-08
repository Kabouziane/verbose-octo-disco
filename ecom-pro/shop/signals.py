from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Customer, Order
import uuid

@receiver(post_save, sender=User)
def create_customer_profile(sender, instance, created, **kwargs):
    """Créer automatiquement un profil client lors de la création d'un utilisateur"""
    if created:
        Customer.objects.create(user=instance)

@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    """Générer automatiquement un numéro de commande unique"""
    if not instance.order_number:
        instance.order_number = f"CMD{uuid.uuid4().hex[:8].upper()}"