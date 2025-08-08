from django.urls import path
from MainApp.views import (index_page, add_snippet_page, snippet_detail,
                           edit_snippet_page, delete_snippet_page, custom_login, custom_logout, snippets_list,
                           custom_registration, comment_add, search_snippets, snippets_stats, snippets_by_tag, my_snippets,
                           user_notifications, mark_notification_read)

app_name = 'MainApp'

urlpatterns = [
    path('', index_page, name="home"),
    path('snippets/', snippets_list, name='snippets-list'),
    path('my-snippets/', my_snippets, name='user-snippets'),
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

    # Notifications
    path('notifications/', user_notifications, name='notifications'),
    path('notifications/mark-read/<int:pk>/', mark_notification_read, name='mark_notification_read'),
]