from django.db import models
from django.contrib.auth.models import User

STATE_CHOICES = [
    ('pending', 'Pendiente'), 
    ('doing', 'En proceso'), 
    ('complete', 'Completada')
]

class Task(models.Model):
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(verbose_name='Descripción', blank=True, null=True)
    expiration_date = models.DateField(verbose_name='Fecha de vencimiento', blank=True, null=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=20, default='pending')
    user = models.ForeignKey(User, related_name='tasks', on_delete=models.PROTECT)

    def __str__(self):
        return self.title
