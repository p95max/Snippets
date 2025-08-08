from MainApp.forms import SnippetSearchForm
from MainApp.models import Notification


def search_form(request):
    return {'search_form': SnippetSearchForm(request.GET)}

def unread_notifications_count(request):
    if request.user.is_authenticated:
        from MainApp.models import Notification
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}