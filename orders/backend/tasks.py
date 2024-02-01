from django.core.mail import EmailMultiAlternatives
# from orders.celery import application as celery
from celery import shared_task
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from orders.settings import EMAIL_HOST_USER

# @celery.task
# def send_msg(subject, body, from_email, to_email):
#     msg = EmailMultiAlternatives(subject, body, from_email, to_email)
#     msg.send()


@shared_task()
def send_msg(subject, body, to_email, from_email=EMAIL_HOST_USER):
    msg = EmailMultiAlternatives(subject, body, from_email, to_email)
    msg.send()


@shared_task()
def import_data(shop_id, data):
    shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
    for category in data['categories']:
        category_obj, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_obj.shops.add(shop.id)
        category_obj.save()
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in data['goods']:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
        product_info = ProductInfo.objects.create(
            product_id=product.id,
            model=item['model'],
            price=item['price'],
            price_rrc=item['price_rrc'],
            quantity=item['quantity'],
            shop_id=shop.id
        )
        for name, value in item['parameters'].items():
            parameter_obj, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(
                product_info_id=product_info.id,
                parameter_id=parameter_obj.id,
                value=value
            )
    # shop.name = data['shop']
    # shop.is_uptodate = True
    # shop.save()
