from rest_framework import serializers
from .models import Category, Product, ProductImage, Customer, Address, Cart, CartItem, Order, OrderItem, Wishlist

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_with_vat = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_in_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = '__all__'

    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'subtotal', 'added_at']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'customer', 'items', 'total_amount', 'items_count', 'created_at', 'updated_at']

    def get_items_count(self, obj):
        return obj.items.count()

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    vat_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source='customer.user.get_full_name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'billing_address', 'shipping_address', 'payment_method', 'notes', 'items']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        total_amount = 0
        vat_amount = 0
        
        for item_data in items_data:
            item = OrderItem.objects.create(order=order, **item_data)
            total_amount += item.subtotal
            vat_amount += item.vat_amount
        
        order.total_amount = total_amount
        order.vat_amount = vat_amount
        order.save()
        
        return order

class WishlistSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Wishlist
        fields = ['id', 'customer', 'products', 'products_count', 'created_at']

    def get_products_count(self, obj):
        return obj.products.count()