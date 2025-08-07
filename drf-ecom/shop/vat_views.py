from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .vat_validator import validate_vat_number

@api_view(['POST'])
@permission_classes([AllowAny])
def validate_vat_api(request):
    """API publique pour valider un numéro de TVA"""
    vat_number = request.data.get('vat_number', '')
    
    if not vat_number:
        return Response(
            {'error': 'Numéro de TVA requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    print(f"Validation TVA pour: {vat_number}")
    result = validate_vat_number(vat_number)
    print(f"Résultat: {result}")
    return Response(result)