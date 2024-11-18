from rest_framework.test import APIClient
from django.test import TestCase
from django.contrib.auth.models import User
from .models import Task

class UserAPITest(TestCase):
    def test_signup(self):
        data = {
            'username': 'user',
            'password': 'password'
        }
        response = self.client.post('/api/signup/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.get(username=response.data['username']))

    def test_login_and_refresh(self):
        data = {
            'username': 'user',
            'password': 'password'
        }
        User.objects.create_user(**data)
        response = self.client.post('/api/login/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('refresh' in response.data)
        self.assertTrue('access' in response.data)
        response = self.client.post('/api/token/refresh/', { 'refresh': response.data['refresh'] }, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('access' in response.data)


class TaskAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user', password='password')
        self.client.force_authenticate(user=self.user)

    def test_create_task_api(self):
        data = {
            'title': 'Tarea de prueba',
            'description': 'Descripción de la tarea',
            'expiration_date': '2024-11-17',
            'state': 'pending'
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        task = Task.objects.get(id=response.data['id'])
        self.assertEqual(data['title'], task.title)
        self.assertEqual(data['description'], task.description)
        self.assertEqual(data['expiration_date'], task.expiration_date.strftime('%Y-%m-%d'))
        self.assertEqual(data['state'], task.state)
        self.assertEqual(self.user.id, task.user.id)

    def test_list_tasks(self):
        Task.objects.create(title='Tarea 1', user=self.user, state='pending')
        Task.objects.create(title='Tarea 2', user=self.user, state='doing')
        user2 = User.objects.create_user(username='user2', password='password2')
        Task.objects.create(title='Tarea de otro usuario', user=user2)
        response = self.client.get('/api/tasks/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

    def test_filter_tasks_by_state(self):
        Task.objects.create(title='Pendiente', user=self.user, state='pending')
        Task.objects.create(title='En progreso', user=self.user, state='doing')
        response = self.client.get('/api/tasks/?state=pending', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['state'], 'pending')

    def test_get_task_details(self):
        task = Task.objects.create(title='Tarea de prueba', user=self.user)
        response = self.client.get(f'/api/tasks/{task.id}/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Tarea de prueba')

    def test_update_task(self):
        task = Task.objects.create(title='Tarea inicial', user=self.user)
        data = { 'title': 'Tarea actualizada', 'state': 'doing' }
        response = self.client.put(f'/api/tasks/{task.id}/', data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Tarea actualizada')
        self.assertEqual(response.data['state'], 'doing')

    def test_delete_task(self):
        task = Task.objects.create(title='Tarea para eliminar', user=self.user)
        response = self.client.delete(f'/api/tasks/{task.id}/', format='json')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(id=task.id).exists())

    def test_cannot_access_other_users_task(self):
        user2 = User.objects.create_user(username='user2', password='password2')
        task = Task.objects.create(title='Tarea de otro usuario', user=user2)
        response = self.client.get(f'/api/tasks/{task.id}/', format='json')
        self.assertEqual(response.status_code, 404)

    def test_task_without_title(self):
        data = {
            'description': 'Descripción de la tarea',
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_task_with_long_title(self):
        title = "T" * 201
        data = {
            'title': title,
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('title', response.data)

    def test_invalid_state(self):
        data = {
            'title': 'Estado erróneo',
            'state': 'bad_state'
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('state', response.data)
        
    def test_invalid_expiration_date_format(self):
        data = {
            'title': 'Tarea inválida',
            'expiration_date': 'fecha-invalida',
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('expiration_date', response.data)

