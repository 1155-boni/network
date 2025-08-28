from .models import Message

def global_unread_count(request):
    if request.user.is_authenticated:
        return {
            "global_unread_count": Message.objects.filter(
                receiver=request.user, is_read=False
            ).count()
        }
    return {}