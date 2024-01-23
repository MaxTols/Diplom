from django.shortcuts import render, get_object_or_404
from orders import settings
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Shop, Category, Product, ProductInfo, Contact, ConfirmEmailToken
from .serializers import CategorySerializer, ShopSerializer, ProductSerializer, ProductInfoSerializer, \
    ContactSerializer, UserSerializer
from .signals import new_user_registered_signal


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductView(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductInfoView(ListAPIView):
    def get(self, request, *arg, **kwargs):
        shop_id = request.GET.get("shop_id")
        category_id = request.GET.get("category_id")
        product_id = request.GET.get("product_id")
        li = {'shop_id': shop_id, 'category_id': category_id, 'product_id': product_id}

        if shop_id is None or category_id is None or product_id is None:
            return Response(f"Не указан {[i for i, j in li.items() if j is None]}")
        else:
            queryset = ProductInfo.objects.filter(
                shop_id=shop_id, product__category_id=category_id, product_id=product_id)
            serializer = ProductInfoSerializer(queryset, many=True)
            return Response(serializer.data)


class RegisterUserView(APIView):
    def post(self, request, *args, **kwargs):
        if {'first_name', 'last_name', 'email', 'password', 'username'}.issubset(request.data):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                user.set_password(user.password)
                user.save()
                return Response('User register')
            else:
                return Response(serializer.errors)
        return Response('Not all arguments!')


class ConfirmUserView(APIView):
    def post(self, request, *arg, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()

            if token:
                token.save()
                return Response('Good')
            else:
                return Response('Bad')
        else:
            return Response('Very Bad')


class AccountDetailsView(APIView):
    def get(self, request, *arg, **kwargs):
        ...

    def post(self, request, *arg, **kwargs):
        ...


class LoginAccount(APIView):
    def post(self, request, *arg, **kwargs):
        ...


class ContactView(APIView):
    def get(self, request, *arg, **kwargs):
        # if not request.user.is_authenticated:
        #     return Response('Log in required', status=403)
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        li = ['phone', 'city', 'street', 'house', 'building', 'structure', 'apartment']
        if li in request.data:
            request.data.update(user_id=request.user.id)
            serializer = ContactSerializer(data=request.data)
            # if serializer.is_valid():
            #     serializer.save()
            return Response(serializer.data)
            # else:
            #     return Response(serializer.errors)
        return Response('Указан не полный адрес')

    def put(self, request, *arg, **kwargs):
        contact = Contact.objects.filter(user_id=request.user.id)
        if contact:
            serializer = ContactSerializer(contact, data=request.data)
            return Response(serializer.data)

    def delete(self, request, *arg, **kwargs):
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, data=request.data)
        return Response(serializer.data)
