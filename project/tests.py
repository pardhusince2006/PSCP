from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Project, Notification, Team
from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date, timedelta
from django.contrib.messages import get_messages

# Create your tests here.

class ProjectModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123',
            is_staff=True
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )

    def test_project_creation(self):
        project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            deadline=date.today() + timedelta(days=7),
            created_by=self.teacher
        )
        self.assertEqual(str(project), 'Test Project')
        self.assertEqual(project.is_submitted, False)
        self.assertIsNone(project.score)

class NotificationModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123',
            is_staff=True
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            deadline=date.today() + timedelta(days=7),
            created_by=self.teacher
        )

    def test_notification_creation(self):
        notification = Notification.objects.create(
            user=self.teacher,
            sender=self.student,
            project=self.project,
            message='Test notification',
            notification_type='join_request'
        )
        self.assertEqual(str(notification), f'Notification for {self.teacher.username} - Test notification')
        self.assertEqual(notification.status, 'pending')
        self.assertFalse(notification.is_read)

class TeamModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123',
            is_staff=True
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            deadline=date.today() + timedelta(days=7),
            created_by=self.teacher
        )

    def test_team_creation(self):
        team = Team.objects.create(
            project=self.project,
            created_by=self.teacher,
            status='Approved'
        )
        team.members.add(self.student)
        self.assertEqual(str(team), f'Team for {self.project.title}')
        self.assertEqual(team.status, 'Approved')
        self.assertTrue(self.student in team.members.all())

class ProjectViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123',
            is_staff=True
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            deadline=date.today() + timedelta(days=7),
            created_by=self.teacher
        )

    def test_project_creation_view(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(reverse('project:create_project'), {
            'title': 'New Project',
            'description': 'New Description',
            'deadline': date.today() + timedelta(days=14)
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Project.objects.filter(title='New Project').exists())

    def test_project_evaluation_view(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(
            reverse('project:evaluate_project', args=[self.project.id]),
            {'score': 85}
        )
        self.assertEqual(response.status_code, 302)
        self.project.refresh_from_db()
        self.assertEqual(self.project.score, 85)

    def test_project_evaluation_invalid_score(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(
            reverse('project:evaluate_project', args=[self.project.id]),
            {'score': 150}  # Invalid score
        )
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "❌ Score must be between 0-100")

    def test_project_evaluation_non_staff(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('project:evaluate_project', args=[self.project.id]),
            {'score': 85}
        )
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Only teachers can evaluate projects.")

    def test_project_info_view(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('project:project_info', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'project_info.html')

    def test_join_project_view(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('project:join_project', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Notification.objects.filter(
            project=self.project,
            sender=self.student,
            notification_type='join_request'
        ).exists())

    # def test_join_project_already_requested(self):
    #     # First request
    #     self.client.login(username='student', password='testpass123')
    #     response = self.client.post(
    #         reverse('project:join_project', args=[self.project.id]),
    #         {'username': 'student'}
    #     )
    #     messages_first = list(get_messages(response.wsgi_request))
    #     self.assertEqual(str(messages_first[0]), "✅ Your request to join the project has been sent successfully. The teacher will review it soon.")
        
    #     # Clear messages
    #     for message in messages_first:
    #         str(message)  # Mark message as read
    
    #     # Second request
    #     response = self.client.post(
    #         reverse('project:join_project', args=[self.project.id]),
    #         {'username': 'student'}
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     messages = list(get_messages(response.wsgi_request))
    #     self.assertEqual(str(messages[0]), "⚠️ You have already sent a request to join this project. Please wait for the teacher's response.")

    def test_create_team_view(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(
            reverse('project:create_team', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')

    def test_collaborate_view_unauthorized(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('project:collaborate', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "You are not authorized to access this page.")

    def test_collaborate_view_authorized(self):
        # Create team and add student
        team = Team.objects.create(
            project=self.project,
            created_by=self.teacher,
            status='Approved'
        )
        team.members.add(self.student)
        
        self.client.login(username='student', password='testpass123')
        response = self.client.get(
            reverse('project:collaborate', args=[self.project.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'collaborate.html')

    def test_send_collaboration_request(self):
        # Create team first
        team = Team.objects.create(
            project=self.project,
            created_by=self.teacher,
            status='Approved'
        )
        team.members.add(self.student)
        
        # Create another student
        other_student = User.objects.create_user(
            username='other_student',
            password='testpass123'
        )
        
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('project:send_collaboration_request', args=[self.project.id, other_student.id])
        )
        self.assertEqual(response.status_code, 302)
        team.refresh_from_db()
        self.assertTrue(other_student in team.members.all())

class NotificationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(
            username='teacher',
            password='testpass123',
            is_staff=True
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='Test Description',
            deadline=date.today() + timedelta(days=7),
            created_by=self.teacher
        )
        self.notification = Notification.objects.create(
            user=self.teacher,
            sender=self.student,
            project=self.project,
            message='Test notification',
            notification_type='join_request'
        )

    def test_handle_notification_accept(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(
            reverse('project:handle_notification', args=[self.notification.id, 'accept'])
        )
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'accepted')
        self.assertTrue(Team.objects.filter(project=self.project).exists())

    def test_handle_notification_reject(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(
            reverse('project:handle_notification', args=[self.notification.id, 'reject'])
        )
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertEqual(self.notification.status, 'rejected')

    def test_handle_notification_unauthorized(self):
        self.client.login(username='student', password='testpass123')
        response = self.client.post(
            reverse('project:handle_notification', args=[self.notification.id, 'accept'])
        )
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "❌ You are not authorized to perform this action.")

    def test_get_notifications(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.get(reverse('project:get_notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('notifications', response.json())

    def test_mark_all_read(self):
        self.client.login(username='teacher', password='testpass123')
        response = self.client.post(reverse('project:mark_all_read'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'success'})
