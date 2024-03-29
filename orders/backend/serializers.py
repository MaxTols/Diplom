from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import (
    User,
    Shop,
    Category,
    Product,
    ProductInfo,
    Parameter,
    ProductParameter,
    Order,
    OrderItem,
    Contact,
)


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ("id", "name", "url", "status")
        read_only_fields = ("id",)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = ("id",)


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name", "category")
        read_only_fields = ("id",)


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ("id", "name")
        read_only_fields = ("id",)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer(read_only=True)

    class Meta:
        model = ProductParameter
        fields = ("id", "parameter", "value")
        read_only_fields = ("id",)


class ContactSerializer(serializers.ModelSerializer):
    def validate(self, data):
        max_contacts = 5
        data = super().validate(data)
        contacts_count = Contact.objects.filter(user_id=data["user"].id).count()
        if contacts_count >= max_contacts:
            raise ValidationError(f"You have maximum contacts: {max_contacts}")
        return data

    class Meta:
        model = Contact
        fields = (
            "id",
            "city",
            "street",
            "house",
            "building",
            "structure",
            "apartment",
            "user",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"user": {"write_only": True}}


class UserSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "username",
            "phone",
            "type",
            "contact",
            "avatar_thumbnail"
        )
        read_only_fields = ("id",)


class ProductInfoSerializer(serializers.ModelSerializer):
    product_parameters = ProductParameterSerializer(read_only=True, many=True)
    product = ProductSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = (
            "id",
            "model",
            "quantity",
            "price",
            "price_rrc",
            "shop",
            "product",
            "product_parameters",
        )
        read_only_fields = ("id",)


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ("id", "quantity", "order", "product_info")
        read_only_fields = ("id",)


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemCreateSerializer(read_only=True, many=True)
    total_sum = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ("id", "total_sum", "dt", "status", "user", "order_items")
        read_only_fields = ("id",)
