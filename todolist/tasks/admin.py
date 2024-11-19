from django.contrib import admin
from .models import Task, Tag

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'expiration_date', 'state', 'user', 'parent_task')
    raw_id_fields = ('user', 'parent_task')


@admin.register(Tag)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
