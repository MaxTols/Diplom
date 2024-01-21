from rest_framework import serializers

from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'url')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'shop')
        read_only_fields = ('id',)


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'name', 'category')
        read_only_fields = ('id',)


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'name', 'shop', 'product', 'quantity', 'price', 'price_rrc')
        read_only_fields = ('id',)


# class ParameterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Parameter
#         fields = ('id', 'name')
#         read_only_fields = ('id',)
#
#
# class ProductParameterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ProductParameter
#         fields = ('id', 'value')
#         read_only_fields = ('id',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ('id', 'phone', 'city', 'street', 'house', 'building', 'structure', 'apartment',)
        read_only_fields = ('id',)


class UserSerializer(serializers.ModelSerializer):
    contacts = ContactSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'surname', 'name', 'email', 'contacts')
        read_only_fields = ('id',)


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'dt', 'status', 'user')
        read_only_fields = ('id',)


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    product_info = ProductInfoSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'order', 'shop', 'product_info', 'quantity')
        read_only_fields = ('id',)
