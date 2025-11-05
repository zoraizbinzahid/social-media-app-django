from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)[:50]
    return render(request, 'notifications/list.html', {'notifications': notifications})

@login_required
def api_notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)[:20]
    
    notification_data = []
    for notification in notifications:
        notification_data.append({
            'id': notification.id,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'sender_name': notification.sender.username if notification.sender else None,
            'sender_profile_pic': notification.sender.profile.profile_pic.url if notification.sender and hasattr(notification.sender, 'profile') and notification.sender.profile.profile_pic else None,
            'timestamp': notification.created_at.strftime('%b %d, %Y %I:%M %p'),
            'unread': not notification.is_read,
            'post_id': notification.post.id if notification.post else None,
        })
    
    return JsonResponse({'notifications': notification_data})

@login_required
def mark_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, recipient=request.user)
    notification.is_read = True
    notification.save()
    return JsonResponse({'success': True})

@login_required
def test_notification(request):
    from .utils import create_notification
    create_notification(
        recipient=request.user,
        notification_type='test',
        message="This is a test notification!",
        sender=request.user
    )
    return JsonResponse({'success': True, 'message': 'Test notification created'})