from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from .tasks import send_msg_task


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    send_msg_task.delay(
        f"Password Reset Token for {reset_password_token.user}",
        reset_password_token.key,
        [reset_password_token.user.email],
    )
