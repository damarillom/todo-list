from celery import shared_task
from django.core.mail import send_mail
from .models import Task
from datetime import date

@shared_task
def send_reminder_emails():
    tasks = Task.objects.filter(expiration_date=date.today(), state='pending')
    for task in tasks:
        send_mail(
            subject="Recordatorio de Tarea Pendiente",
            message=f"Hola {task.user.username}, recuerda completar tu tarea: {task.title}.",
            from_email="noreply@example.com",
            recipient_list=[task.user.email],
        )