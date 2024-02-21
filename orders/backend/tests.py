import os

import pytest
from backend.models import User, Shop, Category, Product, ProductInfo
from django.urls import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker

PATH_PREFIX = "http://127.0.0.1:8000/backend/"


def full_path(relative_path: str) -> str:
    return PATH_PREFIX + relative_path


valid_user_data = {
    "email": "seller@mail.ru",
    "password": "wl;ef;lwnefd",
    "first_name": "Max",
    "last_name": "Tols",
    "phone": "9051234567",
}

test_data_register_user = [
    [valid_user_data, status.HTTP_201_CREATED, "Регистрация с корректными данными"],
    [
        {key: valid_user_data[key] for key in ["email", "password"]},
        status.HTTP_400_BAD_REQUEST,
        "Регистрация с неполными данными",
    ],
    [
        {**valid_user_data, **dict(email="email")},
        status.HTTP_400_BAD_REQUEST,
        "Некорректный email",
    ],
    [
        {**valid_user_data, **dict(password="1234")},
        status.HTTP_400_BAD_REQUEST,
        "Некорректный пароль",
    ],
]

test_data_only_for_shops = [
    ["seller/update/", "post"],
    ["seller/status/", "get"],
    ["seller/status/", "post"],
    ["seller/orders/", "get"],
]

valid_update_data = {
    "file": os.path.join(os.path.dirname(settings.BASE_DIR), "orders/fixtures/shop.yaml"),
    "url": "https://raw.githubusercontent.com/netology-code/pd-diplom/master/data/shop1.yaml",
}
test_data_update_price_info = [
    [
        valid_update_data["file"],
        valid_update_data["url"],
        status.HTTP_200_OK,
        "Корректные данные",
    ],
    [valid_update_data["file"], None, status.HTTP_200_OK, "Только файл"],
    [None, valid_update_data["url"], status.HTTP_200_OK, "Только url"],
    [None, None, status.HTTP_400_BAD_REQUEST, "Данные не переданы"],
]


@pytest.mark.django_db
class TestSeller:
    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def valid_user(self):
        return User.objects.create_user(
            valid_user_data["email"], valid_user_data["password"]
        )

    @pytest.fixture
    def valid_seller(self, valid_user):
        valid_user.type = "SP"
        valid_user.save()
        return valid_user

    @pytest.mark.parametrize(
        "data, expected_status, description", test_data_register_user
    )
    def test_register_user(self, api_client, data, expected_status, description):
        count = User.objects.count()

        response = api_client.post(full_path("user/register/"), data=data)

        assert response.status_code == expected_status, description
        if response.status_code == status.HTTP_201_CREATED:
            assert (
                User.objects.count() == count + 1
            ), "Количество пользователей должно увеличиться"

    def test_register_user_with_existing_email(self, api_client, valid_user):
        response = api_client.post(
            full_path("user/register/"), data=valid_user_data
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "Email уже зарегистрирован"

    @pytest.mark.parametrize("path, method", test_data_only_for_shops)
    def test_only_for_shops(self, api_client, valid_user, path, method):
        api_client.force_authenticate(valid_user)

        response = getattr(api_client, method)(full_path(path))

        assert (
            response.status_code == status.HTTP_403_FORBIDDEN
        ), "Не является магазином"

    @pytest.mark.parametrize(
        "file_path, url, expected_status, description", test_data_update_price_info
    )
    def test_price_info(
        self, api_client, valid_seller, file_path, url, expected_status, description
    ):
        api_client.force_authenticate(valid_seller)

        if file_path:
            with open(file_path, "rb") as fp:
                response = api_client.post(
                    full_path("seller/update/"), {"file": fp}, format="multipart"
                )
        elif url:
            response = api_client.post(
                full_path("seller/update/"), {"url": url}, format="multipart"
            )
        else:
            response = api_client.post(
                full_path("seller/update/"),
            )

        assert response.status_code == expected_status, description


# @pytest.fixture
# def shop_factory():
#     def factory(*args, **kwargs):
#         return baker.make(Shop, *args, **kwargs)
#
#     return factory


# @pytest.fixture
# def client():
#     return APIClient()


# @pytest.mark.django_db
# def test_shop(client, shop_factory):
#     shop = shop_factory(_quantity=1)
#     response = client.get(full_path("shops/"))
#     assert response.status_code == 200
#     for i, v in enumerate(response.data):
#         assert v["name"] == shop[i].name


# @pytest.mark.django_db
# def test_shops(client):
#     User.objects.create_user("admin")
#     response = client.post(full_path("shops/"), data={"user": 1, "name": "MEGA"})
#     assert response.status_code == 201
