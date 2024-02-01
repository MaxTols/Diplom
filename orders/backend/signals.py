from typing import Type

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
from .tasks import send_msg
from .models import ConfirmEmailToken, User

# new_order = Signal()
# new_user_registered = Signal()


# @receiver(post_save, sender=User)
# def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
#     if created and not instance.is_active:
#         token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
#         msg = EmailMultiAlternatives(
#             f"Token for {instance.email}", token.key, settings.EMAIL_HOST_USER, [instance.email])
#         msg.send()


# @receiver(post_save, sender=User)
# def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
#     if created and not instance.is_active:
#         token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
#         send_msg.delay(
#             subject=f'Token for {instance.email}',
#             body=f'Is your TOKEN: "{token.key}"',
#             from_email=settings.EMAIL_HOST_USER,
#             to_email=[instance.email],
#         )

# @receiver(new_order)
# def new_order_signal(user_id, **kwargs):
#     user = User.objects.get(id=user_id)
#     msg = EmailMultiAlternatives(
#         "Updating the order status", 'The order has been formed', settings.EMAIL_HOST_USER, [user.email])
#     msg.send()


# @receiver(new_order)
# def new_order_signal(user_id, **kwargs):
#     user = User.objects.get(id=user_id)
#     send_msg.delay(
#         subject='Updating the order status',
#         body='The order has been formed',
#         from_email=settings.EMAIL_HOST_USER,
#         to_email=[user.email]
#     )


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    msg = EmailMultiAlternatives(
        f"Password Reset Token for {reset_password_token.user}",
        reset_password_token.key,
        settings.EMAIL_HOST_USER,
        [reset_password_token.user.email]
    )
    msg.send()
