from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction, IntegrityError
from .models import Customer
import uuid
import logging

logger = logging.getLogger(__name__)

class CustomerCreateSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    is_business = serializers.BooleanField(default=False)
    company_name = serializers.CharField(required=False, allow_blank=True)
    company_address = serializers.CharField(required=False, allow_blank=True)
    vat_number = serializers.CharField(required=False, allow_blank=True)
    iban = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'email', 'phone', 'is_business', 'company_name', 'company_address', 'vat_number', 'iban']

    def validate_email(self, value):
        """Validation de l'email"""
        if not value:
            raise serializers.ValidationError("L'email est obligatoire")
        
        # Vérifier si un utilisateur avec cet email existe déjà
        from django.contrib.auth.models import User
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un utilisateur avec cet email existe déjà")
        
        return value

    def validate(self, data):
        """Validation globale des données"""
        # Si c'est un particulier, prénom et nom obligatoires
        if not data.get('is_business', False):
            if not data.get('first_name', '').strip():
                raise serializers.ValidationError({'first_name': 'Prénom obligatoire pour les particuliers'})
            if not data.get('last_name', '').strip():
                raise serializers.ValidationError({'last_name': 'Nom obligatoire pour les particuliers'})
        
        # Si c'est une entreprise, nom d'entreprise obligatoire
        if data.get('is_business', False):
            if not data.get('company_name', '').strip():
                raise serializers.ValidationError({'company_name': 'Nom d\'entreprise obligatoire'})
        
        return data

    def create(self, validated_data):
        """Création sécurisée du client"""
        email = validated_data['email']
        
        try:
            with transaction.atomic():
                # Générer un username unique
                username = f"{email.split('@')[0]}_{uuid.uuid4().hex[:8]}"
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=validated_data.get('first_name', '').strip(),
                    last_name=validated_data.get('last_name', '').strip(),
                )
                
                # Créer UN SEUL client
                customer = Customer.objects.create(
                    user=user,
                    phone=validated_data.get('phone', '').strip(),
                    is_business=validated_data.get('is_business', False),
                    company_name=validated_data.get('company_name', '').strip(),
                    company_address=validated_data.get('company_address', '').strip(),
                    vat_number=validated_data.get('vat_number', '').strip(),
                    iban=validated_data.get('iban', '').strip(),
                )
                
                logger.info(f"Client unique créé: {customer.id} - {customer.is_business}")
                return customer
                
        except Exception as e:
            logger.error(f"Erreur création: {e}")
            raise serializers.ValidationError({'non_field_errors': f'Erreur: {str(e)}'})