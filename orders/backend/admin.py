from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Shop, Category, Product, ProductInfo, Order, OrderItem, Contact, ConfirmEmailToken


@admin.register(User)
class UserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', ]


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', ]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', ]


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity', 'price', 'price_rrc', ]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['dt', 'status', ]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['quantity', ]


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['phone', 'city', 'street', 'house', 'building', 'structure', 'apartment', ]


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'key', 'created_at', ]
