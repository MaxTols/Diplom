from django.urls import path
from django_rest_passwordreset.views import (
    reset_password_request_token,
    reset_password_confirm,
)
from .views import (
    CategoryView,
    ShopView,
    ProductView,
    ProductInfoView,
    ContactView,
    RegisterUserView,
    OrderView,
    ConfirmUserView,
    AccountDetailsView,
    LoginAccountView,
    BasketView,
    SellerOrdersView,
    SellerStatusView,
    SellerUpdate,
)

app_name = "backend"

urlpatterns = [
    path("user/register/", RegisterUserView.as_view(), name="user-register"),
    path("user/register/confirm/", ConfirmUserView.as_view(), name="user-register-confirm"),
    path("user/login/", LoginAccountView.as_view(), name="user-login"),
    path("user/details/", AccountDetailsView.as_view(), name="user-details"),
    path("user/contact/", ContactView.as_view(), name="user-contact"),
    path("user/reset_password/", reset_password_request_token, name="reset-password"),
    path("user/reset_password/confirm/", reset_password_confirm, name="reset-password-confirm"),
    path("seller/update/", SellerUpdate.as_view(), name="seller-update"),
    path("seller/status/", SellerStatusView.as_view(), name="seller-status"),
    path("seller/orders/", SellerOrdersView.as_view(), name="seller-orders"),
    path("shops/", ShopView.as_view(), name="shops"),
    path("categories/", CategoryView.as_view(), name="categories"),
    path("products/", ProductView.as_view(), name="products"),
    path("product_info/", ProductInfoView.as_view(), name="product_info"),
    path("basket/", BasketView.as_view(), name="basket"),
    path("order/", OrderView.as_view(), name="order"),
]
