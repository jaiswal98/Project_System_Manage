from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from manager.models import Project, Task
from datetime import date

class MainPagesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
        # Create a sample project
        self.project = Project.objects.create(
            name='Test Project',
            description='A test project',
            start_date=date.today(),
            end_date=date.today()
        )

        # Create a sample task
        self.task = Task.objects.create(
            title='Sample Task',
            description='Test task',
            deadline=date.today(),
            status='Pending',
            project=self.project,
            assigned_to=self.user
        )

    def test_login_page_accessible(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_register_page_accessible(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')

    def test_dashboard_redirect_for_anonymous(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/login/?next=/dashboard/')

    def test_dashboard_for_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your Assigned Tasks')

    def test_project_list_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('project_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Projects')

    def test_task_list_page(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Tasks')

    def test_project_detail_view(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('project_detail', args=[self.project.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.name)

    def test_task_completion_action(self):
        self.client.login(username='testuser', password='testpass')
        url = reverse('complete_task', args=[self.task.pk])
        response = self.client.post(url)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'Completed')
