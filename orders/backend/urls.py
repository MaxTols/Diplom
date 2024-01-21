from django.urls import path
from .views import CategoryView, ShopView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='categories'),
    path('shops/', ShopView.as_view(), name='shops'),
]
