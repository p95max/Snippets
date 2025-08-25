from django.views.generic import ListView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, DeleteView
from MainApp.forms import SnippetForm, CommentForm
from MainApp.models import Snippet, Comment, Notification
from MainApp.signals import snippet_views, snippet_deleted


class AddSnippetView(LoginRequiredMixin, CreateView):
    """Создание нового сниппета"""
    model = Snippet
    form_class = SnippetForm
    template_name = 'pages/add_snippet.html'
    success_url = reverse_lazy('snippets-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pagename'] = 'Создание сниппета'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "Success!!!")
        return super().form_valid(form)


class SnippetDetailView(DetailView):
    model = Snippet
    template_name = 'snippet_detail.html'
    context_object_name = 'snippet'
    pk_url_kwarg = 'id'

    def get_queryset(self):
        return Snippet.objects.annotate(num_comments=Count('comments')).select_related('user')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        viewed_key = f'snippet_{self.object.id}'
        comment_form = CommentForm()

        comments = Comment.objects.filter(snippet=self.object).order_by('-creation_date').select_related('author')
        paginator = Paginator(comments, 5)
        page_number = request.GET.get('page')
        comments_page = paginator.get_page(page_number)

        if not request.session.get(viewed_key, False):
            snippet_views.send(sender=Snippet, snippet_id=self.object.id)
            request.session[viewed_key] = True

        self.object.likes_count = self.object.likes.filter(vote=1).count()
        self.object.dislikes_count = self.object.likes.filter(vote=-1).count()
        self.object.user_like = None
        if request.user.is_authenticated:
            user_like_obj = self.object.likes.filter(user=request.user).first()
            if user_like_obj:
                self.object.user_like = user_like_obj.vote

        for comment in comments_page:
            comment.likes_count = comment.likes.filter(vote=1).count()
            comment.dislikes_count = comment.likes.filter(vote=-1).count()
            comment.user_like = None
            if request.user.is_authenticated:
                user_like_obj = comment.likes.filter(user=request.user).first()
                if user_like_obj:
                    comment.user_like = user_like_obj.vote

        context = self.get_context_data(
            comment_form=comment_form,
            comments_page=comments_page,
            pagename=f'Сниппет: {self.object.name}',
        )
        return self.render_to_response(context)


class SnippetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Snippet
    template_name = 'snippet_confirm_delete.html'
    success_url = reverse_lazy('MainApp:user_snippets')

    def test_func(self):
        snippet = self.get_object()
        return snippet.user == self.request.user

    def handle_no_permission(self):
        return HttpResponseForbidden("Вы не можете удалить этот сниппет.")

    def delete(self, request, *args, **kwargs):
        snippet = self.get_object()
        snippet_id = snippet.id
        response = super().delete(request, *args, **kwargs)
        snippet_deleted.send(sender=Snippet, snippet_id=snippet_id)
        return response


class UserNotificationsView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications.html'
    context_object_name = 'notifications'
    paginate_by = 10

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user,
            notification_type__in=['comment', 'like', 'dislike'],
            snippet__isnull=False
        ).select_related('snippet', 'snippet__user').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = self.get_queryset().filter(is_read=False).count()
        context['pagename'] = 'Мои уведомления'
        context['page_obj'] = context['page_obj']
        return context