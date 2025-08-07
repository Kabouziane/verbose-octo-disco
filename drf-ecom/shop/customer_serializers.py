from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer

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

    def validate(self, data):
        # Si c'est un particulier, prénom et nom obligatoires
        if not data.get('is_business', False):
            if not data.get('first_name'):
                raise serializers.ValidationError({'first_name': 'Prénom obligatoire pour les particuliers'})
            if not data.get('last_name'):
                raise serializers.ValidationError({'last_name': 'Nom obligatoire pour les particuliers'})
        
        # Si c'est une entreprise, nom d'entreprise obligatoire
        if data.get('is_business', False):
            if not data.get('company_name'):
                raise serializers.ValidationError({'company_name': 'Nom d\'entreprise obligatoire'})
        
        return data

    def create(self, validated_data):
        from django.db import transaction
        
        email = validated_data['email']
        
        # Vérifier si un client avec cet email existe déjà
        if Customer.objects.filter(user__email=email).exists():
            raise serializers.ValidationError({'email': 'Un client avec cet email existe déjà'})
        
        with transaction.atomic():
            # Créer un nouvel utilisateur avec un username unique
            import uuid
            username = f"{email}_{uuid.uuid4().hex[:8]}"
            
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=validated_data.get('first_name', ''),
                last_name=validated_data.get('last_name', ''),
            )
        
        # Créer le client
        customer_data = {
            'user': user,
            'phone': validated_data.get('phone', ''),
            'is_business': validated_data.get('is_business', False),
            'company_name': validated_data.get('company_name', ''),
            'company_address': validated_data.get('company_address', ''),
            'vat_number': validated_data.get('vat_number', ''),
            'iban': validated_data.get('iban', ''),
        }
        
        customer = Customer.objects.create(**customer_data)
        return customer