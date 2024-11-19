from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from .models import Task, Tag
from .serializers import UserSerializer, TaskSerializer, TagSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner


class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]


class TaskPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    pagination_class = TaskPagination

    def get_queryset(self):
        user = self.request.user
        params = {
            'user': user
        }
        state = self.request.query_params.get('state', None)
        if state:
            params['state'] = state
        expiration_date = self.request.query_params.get('expiration_date', None)
        if expiration_date:
            params['expiration_date'] = expiration_date
        queryset = Task.objects.filter(**params)
        tags = self.request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__name__in=tags).distinct()
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
