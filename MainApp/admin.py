from django.contrib import admin
from django.db.models import Count

from MainApp.models import Snippet, Comment, Tag, Notification


# Snippet
@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang', 'public', 'user', 'creation_date', 'num_comments')
    list_filter = ('lang', 'public', 'creation_date')
    fields = ('name', 'lang', 'code', 'public', 'creation_date', 'user', 'tags')

    search_fields = ('name',)

# Доп.колонка кол-ва комментариев
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            num_comments=Count('comment', distinct=True)
        )
        return queryset

    def num_comments(self, obj):
        return obj.num_comments

    num_comments.short_description = 'Кол-во комментариев'


# Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'snippet', 'creation_date', )
    list_filter = ('author', 'creation_date')

    search_fields = ('text', 'author__username', 'snippet__name')


# Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

    search_fields = ('name',)


# Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'recipient')

    search_fields = ('title', 'recipient')

admin.site.site_header = "PythonBin - администрирование"
admin.site.site_title = "PythonBin Admin"
admin.site.index_title = "Добро пожаловать в администрирование PythonBin"