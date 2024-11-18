from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from .models import Task
from .serializers import UserSerializer, TaskSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import IsOwner
from rest_framework.response import Response

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] 


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
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
