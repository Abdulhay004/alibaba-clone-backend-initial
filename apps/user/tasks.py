
from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

@shared_task
def send_email(email:str, otp_code:str):
    message = render_to_string('emails/email_template.html', {
        'email': email,
        'otp_code': otp_code,
    })

    email_message = EmailMessage(
        'Xizmatimizga hush kelibsiz',
        message,
        settings.EMAIL_HOST_USER,
        [email],
    )
    email_message.content_subtype = 'html'
    try:
        email_message.send(fail_silently=False)
        return 200
    except Exception as e:
        print(f"Email jo'natishda xatolik yuz berdi: {e}")
        return 400