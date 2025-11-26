from django.contrib import admin
from .models import Branch, Category, Product, Stock, Cart, CartItem
from .models import Order, OrderItem

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'latitude', 'longitude', 'phone')
    search_fields = ('name', 'address')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'price')
    search_fields = ('sku', 'name')
    list_filter = ('category',)

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('branch', 'product', 'quantity', 'last_updated')
    list_filter = ('branch', 'product')
    search_fields = ('product__name', 'branch__name')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch', 'created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'added_at')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "branch", "total_price", "created_at")
    list_filter = ("branch", "created_at")

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")

