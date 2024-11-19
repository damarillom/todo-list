from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Tag, Task
from datetime import datetime


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
    

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']
    

class TaskSerializer(serializers.ModelSerializer):
    subtasks = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'expiration_date', 'state', 'user', 'parent_task', 'subtasks', 'tags'
        ]
        read_only_fields = ['user', 'subtasks'] 

    def get_subtasks(self, obj):
        subtasks = Task.objects.filter(parent_task=obj)
        return TaskSerializer(subtasks, many=True).data

    def create(self, validated_data):
        state_choices = [choice[0] for choice in Task._meta.get_field('state').choices]
        if not validated_data.get('title'):
            raise serializers.ValidationError({ 'title': 'La tarea debe tener un título.' })
        elif 1 > len(validated_data.get('title')) > 200:
            raise serializers.ValidationError(
                { 'title': 'El título de la tarea no puede estar en blanco y debe ser menor a 200 carácteres.' }
            )
        elif validated_data.get('state') and validated_data.get('state') not in state_choices:
            raise serializers.ValidationError({ 'state': 'Estado no válido.' })
        elif validated_data.get('expiration_date'):
            try:
                datetime.strptime(str(validated_data.get('expiration_date', '')), '%Y-%m-%d')
            except:
                raise serializers.ValidationError(
                    { 'expiration_date': 'La fecha de expiración debe de tener un el formato YYYY-MM-DD.' }
                )
        tags_data = validated_data.pop('tags', [])
        task = Task.objects.create(**validated_data)
        for tag_data in tags_data:
            if 'name' in tag_data:
                tag, created = Tag.objects.get_or_create(name=tag_data['name'])
                task.tags.add(tag)
        return task
