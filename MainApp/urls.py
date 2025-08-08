from django.urls import path

app_name = 'MainApp'

urlpatterns = [
    path('', 'MainApp.views.index_page', name="home"),
    path('snippets/', 'MainApp.views.snippets_list', name='snippets-list'),
    path('my-snippets/', 'MainApp.views.my_snippets', name='user-snippets'),
    path('snippets/stats/', 'MainApp.views.snippets_stats', name='snippets-stats'),
    path('snippet/<int:id>', 'MainApp.views.snippet_detail', name="snippet-detail"),
    path('search/', 'MainApp.views.search_snippets', name='snippets-search'),
    path('tag/<int:tag_id>/', 'MainApp.views.snippets_by_tag', name='snippets_by_tag'),

    # Custom auth
    path('custom_login/', 'MainApp.views.custom_login', name='custom_login'),
    path('logout/', 'MainApp.views.custom_logout', name='custom_logout'),
    path('regist/', 'MainApp.views.custom_registration', name='custom_regist'),

    # CRUD
    path('snippets/add', 'MainApp.views.add_snippet_page', name="snippet-add"),
    path('snippet/<int:pk>/edit', 'MainApp.views.edit_snippet_page', name="snippet-edit"),
    path('snippet/<int:pk>/delete', 'MainApp.views.delete_snippet_page', name="snippet-delete"),

    # Comments
    path('comment/add', 'MainApp.views.comment_add', name='comment_add'),

    # Notifications
    path('notifications/', 'MainApp.views.user_notifications', name='notifications'),
    path('notifications/mark-read/<int:pk>/', 'MainApp.views.mark_notification_read', name='mark_notification_read'),

    # API endpoints
    path('api/simple-data/', 'MainApp.views_api.simple_api_view', name='simple_api'),
    path('api-test/', 'MainApp.views_api.api_test_page', name='api_test_page'),
]