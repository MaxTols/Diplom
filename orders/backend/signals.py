from typing import Type

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from .models import ConfirmEmailToken, User


@receiver(post_save, sender=User)
def new_user_registered(sender: Type[User], instance: User, created: bool, **kwargs):
    if created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        msg = EmailMultiAlternatives(f"Token for {instance.email}", token.key, settings.EMAIL_HOST_USER, [instance.email])
        msg.send()
