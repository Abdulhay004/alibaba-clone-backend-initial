
from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_email):
    send_mail(
        'Xush kelibsiz!',
        'Bizning platformaga xush kelibsiz!',
        'tolibjonovabdulhay200@gmail.com',
        [user_email],
        fail_silently=False,
    )