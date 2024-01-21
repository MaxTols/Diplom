from django.contrib import admin

from .models import User, Shop, Category, Product, ProductInfo, Order, OrderItem, Contact


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    ...


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    ...


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    ...


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    ...


@admin.register(ProductInfo)
class ProductInfoAdmin(admin.ModelAdmin):
    ...


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ...


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    ...


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    ...
