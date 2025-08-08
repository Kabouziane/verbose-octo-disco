from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import (
    Category, Product, Customer, Cart, CartItem, 
    Order, OrderItem, Wishlist, WishlistItem
)

class CustomerTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )

    def test_create_business_customer(self):
        """Test création d'un client professionnel"""
        data = {
            'user_email': 'business@example.com',
            'user_first_name': 'Business',
            'user_last_name': 'User',
            'is_business': True,
            'company_name': 'Test Company',
            'vat_number': 'BE0123456789',
            'phone': '+32123456789',
            'address': '123 Test Street',
            'city': 'Brussels',
            'postal_code': '1000',
            'country': 'Belgium'
        }
        
        response = self.client.post('/api/shop/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        customer = Customer.objects.get(id=response.data['id'])
        self.assertTrue(customer.is_business)
        self.assertEqual(customer.company_name, 'Test Company')
        self.assertEqual(customer.vat_number, 'BE0123456789')

    def test_create_individual_customer(self):
        """Test création d'un client particulier"""
        data = {
            'user_email': 'individual@example.com',
            'user_first_name': 'John',
            'user_last_name': 'Doe',
            'is_business': False,
            'phone': '+32123456789',
            'address': '456 Test Avenue',
            'city': 'Antwerp',
            'postal_code': '2000',
            'country': 'Belgium'
        }
        
        response = self.client.post('/api/shop/customers/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        customer = Customer.objects.get(id=response.data['id'])
        self.assertFalse(customer.is_business)
        self.assertIsNone(customer.company_name)
        self.assertIsNone(customer.vat_number)

    def test_vat_validation(self):
        """Test validation du numéro de TVA"""
        response = self.client.post('/api/shop/customers/validate_vat/', {
            'vat_number': 'BE0123456789'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_valid', response.data)

class ProductTestCase(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )

    def test_create_product(self):
        """Test création d'un produit"""
        data = {
            'name': 'Test Product',
            'description': 'A test product',
            'price': 99.99,
            'category': self.category.id,
            'stock_quantity': 100,
            'sku': 'TEST001',
            'is_active': True
        }
        
        response = self.client.post('/api/shop/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        product = Product.objects.get(id=response.data['id'])
        self.assertEqual(product.name, 'Test Product')
        self.assertEqual(product.price, Decimal('99.99'))
        self.assertEqual(product.category, self.category)

    def test_product_stock_management(self):
        """Test gestion du stock"""
        product = Product.objects.create(
            name='Stock Test Product',
            description='Test stock management',
            price=Decimal('50.00'),
            category=self.category,
            stock_quantity=10,
            sku='STOCK001'
        )
        
        # Test stock suffisant
        self.assertTrue(product.stock_quantity >= 5)
        
        # Simuler une vente
        product.stock_quantity -= 5
        product.save()
        
        self.assertEqual(product.stock_quantity, 5)

class CartTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=100,
            sku='TEST001'
        )
        
        self.cart = Cart.objects.create(user=self.user)

    def test_add_item_to_cart(self):
        """Test ajout d'un article au panier"""
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        
        response = self.client.post(f'/api/shop/cart/{self.cart.id}/add_item/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item = CartItem.objects.get(cart=self.cart, product=self.product)
        self.assertEqual(cart_item.quantity, 2)

    def test_update_cart_item_quantity(self):
        """Test mise à jour de la quantité d'un article"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        
        data = {
            'product_id': self.product.id,
            'quantity': 3
        }
        
        response = self.client.post(f'/api/shop/cart/{self.cart.id}/add_item/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 4)  # 1 + 3

    def test_remove_item_from_cart(self):
        """Test suppression d'un article du panier"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
        response = self.client.post(f'/api/shop/cart/{self.cart.id}/remove_item/', {
            'product_id': self.product.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

class OrderTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.customer = Customer.objects.create(
            user=self.user,
            is_business=False,
            user_email='test@example.com',
            phone='+32123456789',
            address='123 Test Street',
            city='Brussels',
            postal_code='1000',
            country='Belgium'
        )
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=100,
            sku='TEST001'
        )

    def test_create_order(self):
        """Test création d'une commande"""
        data = {
            'customer': self.customer.id,
            'shipping_address': {
                'street': '123 Test Street',
                'city': 'Brussels',
                'postal_code': '1000',
                'country': 'Belgium'
            },
            'items': [
                {
                    'product': self.product.id,
                    'quantity': 2,
                    'unit_price': 99.99
                }
            ]
        }
        
        response = self.client.post('/api/shop/orders/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        order = Order.objects.get(id=response.data['id'])
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_amount, Decimal('199.98'))

    def test_order_status_update(self):
        """Test mise à jour du statut de commande"""
        order = Order.objects.create(
            customer=self.customer,
            status='pending',
            total_amount=Decimal('199.98'),
            shipping_address={'street': '123 Test Street'}
        )
        
        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=Decimal('99.99')
        )
        
        # Simuler le passage en "processing"
        order.status = 'processing'
        order.save()
        
        self.assertEqual(order.status, 'processing')

class WishlistTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(
            name='Electronics',
            description='Electronic products'
        )
        
        self.product = Product.objects.create(
            name='Test Product',
            description='A test product',
            price=Decimal('99.99'),
            category=self.category,
            stock_quantity=100,
            sku='TEST001'
        )
        
        self.wishlist = Wishlist.objects.create(
            user=self.user,
            name='My Wishlist'
        )

    def test_add_product_to_wishlist(self):
        """Test ajout d'un produit à la wishlist"""
        data = {
            'product_id': self.product.id
        }
        
        response = self.client.post(f'/api/shop/wishlist/{self.wishlist.id}/add_item/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        wishlist_item = WishlistItem.objects.get(wishlist=self.wishlist, product=self.product)
        self.assertEqual(wishlist_item.product, self.product)

    def test_remove_product_from_wishlist(self):
        """Test suppression d'un produit de la wishlist"""
        wishlist_item = WishlistItem.objects.create(
            wishlist=self.wishlist,
            product=self.product
        )
        
        response = self.client.post(f'/api/shop/wishlist/{self.wishlist.id}/remove_item/', {
            'product_id': self.product.id
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(WishlistItem.objects.filter(id=wishlist_item.id).exists())