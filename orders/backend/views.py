from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from orders import settings
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from .models import Shop, Category, Product, ProductInfo, Contact, ConfirmEmailToken
from .serializers import CategorySerializer, ShopSerializer, ProductSerializer, ProductInfoSerializer, \
    ContactSerializer, UserSerializer
from .signals import new_user_registered


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
        list_id = {'shop_id': shop_id, 'category_id': category_id, 'product_id': product_id}
        for key, value in list_id.items():
            if value is None:
                return Response(f'Not added {key}')
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
                return Response('User registered')
            else:
                return Response(serializer.errors)
        return Response('Not added all arguments')


class ConfirmUserView(APIView):
    def post(self, request, *arg, **kwargs):
        if {'email', 'token'}.issubset(request.data):
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()

            if token:
                token.user.save()
                token.delete()
                return Response('Good')
            else:
                return Response('Incorrectly token or email')
        else:
            return Response('No added all values')


class AccountDetailsView(APIView):
    def get(self, request, *arg, **kwargs):
        if not request.user.is_authenticated:
            return Response('Log in required')

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('Account details is updated')
        else:
            return Response(serializer.errors)


class LoginAccountView(APIView):
    def post(self, request, *args, **kwargs):
        if {'username', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['username'], password=request.data['password'])
            if user is not None:
                token, _ = Token.objects.get_or_create(user=user)
                return Response(token.key)
            else:
                return Response('Incorrectly data')
        else:
            return Response('No added all values')


class ContactView(APIView):
    def get(self, request, *arg, **kwargs):
        contact = Contact.objects.filter(user_id=request.user.id)
        serializer = ContactSerializer(contact, many=True)
        return Response(serializer.data)

    def post(self, request, *arg, **kwargs):
        contact = {'phone', 'city', 'street', 'house', 'building', 'structure', 'apartment'}
        if contact.issubset(request.data):
            request.data.update({'user': request.user.id})
            serializer = ContactSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        return Response('No added all contacts')

    def put(self, request, *arg, **kwargs):
        contact_id = request.data.get('contact_id')
        contact = Contact.objects.filter(id=contact_id, user_id=request.user.id).first()
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('Contact is updated')
        else:
            return Response(serializer.errors)

    def delete(self, request, *arg, **kwargs):
        contact_id = request.data.get('contact_id')
        contact = Contact.objects.filter(id=contact_id, user_id=request.user.id).delete()
        serializer = ContactSerializer(contact, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response('Contact is deleted')


class BasketView(APIView):
    def get(self, request, *arg, **kwargs):
        ...

    def post(self, request, *arg, **kwargs):
        ...

    def put(self, request, *arg, **kwargs):
        ...

    def delete(self, request, *arg, **kwargs):
        ...
