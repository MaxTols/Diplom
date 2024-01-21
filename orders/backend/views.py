from django.shortcuts import render
from rest_framework.generics import ListAPIView
from .models import Category, Shop
from .serializers import CategorySerializer, ShopSerializer


class CategoryView(ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ShopView(ListAPIView):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
