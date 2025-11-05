from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Notification

User = get_user_model()

class NotificationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='testuser1', password='testpass123')
        self.user2 = User.objects.create_user(username='testuser2', password='testpass123')
    
    def test_notification_creation(self):
        notification = Notification.objects.create(
            recipient=self.user1,
            notification_type='test',
            message='Test notification',
            sender=self.user2
        )
        self.assertEqual(notification.recipient, self.user1)
        self.assertEqual(notification.sender, self.user2)
        self.assertEqual(notification.message, 'Test notification')