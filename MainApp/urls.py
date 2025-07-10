from django.urls import path
from MainApp.views import (index_page, add_snippet_page, snippet_detail,
                           edit_snippet_page, delete_snippet_page, custom_login, custom_logout, snippets_universal,
                           custom_registration, comment_add, search_snippets, snippets_stats, snippets_by_tag)
from django.contrib.auth.decorators import login_required

app_name = 'MainApp'

urlpatterns = [
    path('', index_page, name="home"),
    path('snippets/', snippets_universal, name='snippets-list'),
    path('my-snippets/', login_required(lambda r: snippets_universal(r, user_only=True)), name='user_snippets'),
    path('snippets/stats/', snippets_stats, name='snippets-stats'),
    path('snippet/<int:id>', snippet_detail, name="snippet-detail"),
    path('search/', search_snippets, name='snippets-search'),
    path('tag/<int:tag_id>/', snippets_by_tag, name='snippets_by_tag'),

    # Custom auth
    path('custom_login/', custom_login, name='custom_login'),
    path('logout/', custom_logout, name='custom_logout'),
    path('regist/', custom_registration, name='custom_regist'),

    #CRUD
    path('snippets/add', add_snippet_page, name="snippet-add"),
    path('snippet/<int:pk>/edit', edit_snippet_page, name="snippet-edit"),
    path('snippet/<int:pk>/delete', delete_snippet_page, name="snippet-delete"),

    # Comments
    path('comment/add', comment_add, name='comment_add'),
]