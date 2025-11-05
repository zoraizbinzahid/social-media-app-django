def create_notification(recipient, notification_type, message, sender=None, post=None, comment=None):
    """
    Utility function to create notifications
    """
    try:
        from .models import Notification
    except ImportError:
        from notifications.models import Notification
    
    notification = Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        message=message,
        sender=sender,
        post=post,
        comment=comment
    )
    return notification