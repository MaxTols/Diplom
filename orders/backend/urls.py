from django.urls import path
from .views import CategoryView, ShopView, ProductView, ProductInfoView, ContactView, RegisterUserView, \
    ConfirmUserView, AccountDetailsView, LoginAccountView, BasketView, OrderView, ShopOrdersView

urlpatterns = [
    path('categories/', CategoryView.as_view(), name='categories'),
    path('shops/', ShopView.as_view(), name='shops'),
    path('products/', ProductView.as_view(), name='products'),
    path('product_info/', ProductInfoView.as_view(), name='product_info'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('confirm/', ConfirmUserView.as_view(), name='confirm'),
    path('account/', AccountDetailsView.as_view(), name='account'),
    path('login/', LoginAccountView.as_view(), name='login'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('order/', OrderView.as_view(), name='order'),
    path('shop/orders/', ShopOrdersView.as_view(), name='shop_orders'),
]
