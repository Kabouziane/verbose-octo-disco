from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
import stripe
from django.conf import settings
from .vat_validator import validate_vat_number

from .models import Category, Product, Customer, Cart, CartItem, Order, Wishlist
from .serializers import (
    CategorySerializer, ProductSerializer, CustomerSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer,
    WishlistSerializer
)

stripe.api_key = settings.STRIPE_SECRET_KEY

class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['category', 'is_digital']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    lookup_field = 'slug'

    @action(detail=True, methods=['get'])
    def related_products(self, request, slug=None):
        product = self.get_object()
        related = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        serializer = self.get_serializer(related, many=True)
        return Response(serializer.data)

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Customer.objects.filter(user=self.request.user)

    @action(detail=False, methods=['post'])
    def validate_vat(self, request):
        """Valider un numéro de TVA et récupérer les informations entreprise"""
        vat_number = request.data.get('vat_number', '')
        
        if not vat_number:
            return Response(
                {'error': 'Numéro de TVA requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = validate_vat_number(vat_number)
        return Response(result)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Cart.objects.filter(customer=customer)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        serializer = CartItemSerializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        
        cart_item = get_object_or_404(CartItem, cart=cart, product_id=product_id)
        cart_item.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def clear(self, request, pk=None):
        cart = self.get_object()
        cart.items.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Order.objects.filter(customer=customer)

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    @action(detail=True, methods=['post'])
    def create_payment_intent(self, request, pk=None):
        order = self.get_object()
        
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total_amount * 100),  # Stripe utilise les centimes
                currency='eur',
                metadata={'order_id': order.id}
            )
            
            order.stripe_payment_intent_id = intent.id
            order.save()
            
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        order = self.get_object()
        
        if order.stripe_payment_intent_id:
            try:
                intent = stripe.PaymentIntent.retrieve(order.stripe_payment_intent_id)
                
                if intent.status == 'succeeded':
                    order.payment_status = 'paid'
                    order.status = 'confirmed'
                    order.save()
                    
                    # Réduire le stock
                    for item in order.items.all():
                        product = item.product
                        product.stock_quantity -= item.quantity
                        product.save()
                    
                    return Response({'status': 'payment_confirmed'})
                else:
                    return Response(
                        {'error': 'Payment not completed'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except stripe.error.StripeError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(
            {'error': 'No payment intent found'},
            status=status.HTTP_400_BAD_REQUEST
        )

class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        customer = get_object_or_404(Customer, user=self.request.user)
        return Wishlist.objects.filter(customer=customer)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        wishlist.products.add(product)
        
        return Response({'status': 'product_added'})

    @action(detail=True, methods=['delete'])
    def remove_product(self, request, pk=None):
        wishlist = self.get_object()
        product_id = request.data.get('product_id')
        
        product = get_object_or_404(Product, id=product_id)
        wishlist.products.remove(product)
        
        return Response(status=status.HTTP_204_NO_CONTENT)