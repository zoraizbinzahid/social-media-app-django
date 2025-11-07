from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
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
        # Calculate relative time
        now = timezone.now()
        diff = now - notification.created_at
        
        if diff.days > 0:
            if diff.days == 1:
                timestamp = '1 day ago'
            else:
                timestamp = f'{diff.days} days ago'
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            if hours == 1:
                timestamp = '1 hour ago'
            else:
                timestamp = f'{hours} hours ago'
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            if minutes == 1:
                timestamp = '1 minute ago'
            else:
                timestamp = f'{minutes} minutes ago'
        else:
            timestamp = 'Just now'
        
        notification_data.append({
            'id': notification.id,
            'message': notification.message,
            'notification_type': notification.notification_type,
            'sender_name': notification.sender.username if notification.sender else None,
            'sender_profile_pic': notification.sender.profile.profile_pic.url if notification.sender and hasattr(notification.sender, 'profile') and notification.sender.profile.profile_pic else None,
            'timestamp': timestamp,
            'unread': not notification.is_read,
            'post_id': notification.post.id if notification.post else None,
        })
    
    return JsonResponse({'notifications': notification_data})

@login_required
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    if request.method == 'POST':
        updated_count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True)
        
        return JsonResponse({
            'success': True, 
            'message': f'Marked {updated_count} notifications as read',
            'updated_count': updated_count
        })
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@login_required
def mark_as_read(request, notification_id):
    """Mark a single notification as read"""
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id, recipient=request.user)
            notification.is_read = True
            notification.save()
            return JsonResponse({'success': True})
        except Notification.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

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



@login_required
def send_test_websocket(request):
    """Manually send a WebSocket message for testing"""
    try:
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from .models import Notification
        
        channel_layer = get_channel_layer()
        user = request.user
        unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
        
        message_data = {
            'type': 'send_notification',
            'unread_count': unread_count,
            'message': 'TEST: WebSocket is working!',
            'notification_type': 'test'
        }
        
        print(f"🧪 SENDING MANUAL WEBSOCKET TO USER {user.id}: {message_data}")
        
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            message_data
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'WebSocket sent to user {user.id}',
            'unread_count': unread_count
        })
        
    except Exception as e:
        print(f"❌ MANUAL WEBSOCKET ERROR: {e}")
        return JsonResponse({'success': False, 'error': str(e)})