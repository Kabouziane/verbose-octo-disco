from django.contrib import admin
from .models import Category, Product, ProductImage, Customer, Address, Cart, CartItem, Order, OrderItem, Wishlist

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active']
    list_filter = ['category', 'is_active', 'is_digital']
    search_fields = ['name', 'sku']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'is_business', 'created_at']
    list_filter = ['is_business']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'payment_status']
    search_fields = ['order_number', 'customer__user__email']
    readonly_fields = ['order_number', 'created_at']