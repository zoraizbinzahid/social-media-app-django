from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='list'),
    path('api/', views.api_notification_list, name='api_list'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_read'),
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_read'),
    path('test/', views.test_notification, name='test'),  # For testing
]