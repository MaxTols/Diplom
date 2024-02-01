import os
from celery import Celery
# from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")
app = Celery("orders")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# def create_application(namespace):
#     celery = Celery(__package__)
#     celery.config_from_object(settings, namespace=namespace)
#     celery.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
#     return celery
#
#
# application = create_application(namespace="CELERY")
