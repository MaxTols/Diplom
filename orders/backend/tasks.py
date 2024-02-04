from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.core.validators import URLValidator
from celery import shared_task
from requests import get
from yaml import Loader
from yaml import load as load_yaml
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter


@shared_task()
def send_msg_task(subject, body, to_email, from_email=settings.EMAIL_HOST_USER):
    msg = EmailMultiAlternatives(subject, body, from_email, to_email)
    msg.send()


@shared_task()
def import_data_task(url, user_id):
    validate_url = URLValidator()
    validate_url(url)
    stream = get(url).content
    data = load_yaml(stream, Loader=Loader)

    shop, _ = Shop.objects.get_or_create(name=data["shop"], user_id=user_id)
    for category in data["categories"]:
        category_obj, _ = Category.objects.get_or_create(
            id=category["id"], name=category["name"]
        )
        category_obj.shops.add(shop.id)
        category_obj.save()
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in data["goods"]:
        product, _ = Product.objects.get_or_create(
            name=item["name"], category_id=item["category"]
        )
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            model=item["model"],
            price=item["price"],
            price_rrc=item["price_rrc"],
            quantity=item["quantity"],
            shop_id=shop.id,
        )
        for name, value in item["parameters"].items():
            parameter_obj, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=parameter_obj.id,
                value=value,
            )
