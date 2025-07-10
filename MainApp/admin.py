from django.contrib import admin
from MainApp.models import Snippet, Comment, Tag

# Snippet
@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('name', 'lang', 'public', 'user')
    list_filter = ('lang', 'public')
    search_fields = ('name',)
    fields = ('name', 'lang', 'code', 'public', 'user')

# Comment
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('text', 'author', 'snippet', 'creation_date')
    search_fields = ('text', 'author__username', 'snippet__name')
    list_filter = ('author',)

# Tag
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)