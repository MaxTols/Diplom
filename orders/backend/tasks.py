from django.core.mail import EmailMultiAlternatives
from orders.celery import application as celery


@celery.task
def send_msg(subject, body, from_email, to_email):
    msg = EmailMultiAlternatives(subject, body, from_email, to_email)
    msg.send()
