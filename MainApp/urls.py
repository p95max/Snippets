from django.urls import path
from MainApp import views_cbv
from MainApp.views import (index_page, add_snippet_page, snippet_detail,
                           edit_snippet_page, delete_snippet_page, custom_login, custom_logout, snippets_list,
                           custom_registration, comment_add, search_snippets, snippets_stats, snippets_by_tag, my_snippets,
                           user_notifications, unread_notifications_longpoll, mark_notification_read, delete_notification, delete_all_read_notifications,
                           like_comment, like_snippet, user_profile, edit_profile, set_new_userpassword, activate_account, resend_email, subscribe_author,
                           unsubscribe_author)
from MainApp.views_api import simple_api_view, api_test_page


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
    path('set_new_pass', set_new_userpassword, name='set_new_pass'),
    path('activate/<int:user_id>/<str:token>/', activate_account, name='activate_account'),
    path('resend_email/', resend_email, name='resend_email'),

    # Profile
    path('profile/', user_profile, name='user_profile'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('profile/<int:user_id>/', user_profile, name='user_profile_other'),

    #CRUD
    path('snippets/add', add_snippet_page, name="snippet-add"),
    path('snippet/<int:pk>/edit', edit_snippet_page, name="snippet-edit"),
    path('snippet/<int:pk>/delete', delete_snippet_page, name="snippet-delete"),

    # Comments
    path('comment/add', comment_add, name='comment_add'),

    # Notifications
    path('notifications/', user_notifications, name='notifications'),
    path('api/unread-notifications-longpoll/', unread_notifications_longpoll, name='unread_notifications_longpoll'),
    path('notifications/mark-read/<int:notif_id>/', mark_notification_read, name='mark_notification_read'),
    path('notifications/delete/<int:notif_id>/', delete_notification, name='delete_notification'),
    path('notifications/delete-all-read/', delete_all_read_notifications, name='delete_all_read_notifications'),

    # API endpoints
    path('api/simple-data/', simple_api_view, name='simple_api'),
    path('api-test/', api_test_page, name='api_test_page'),

    # Like
    path('like-comment/', like_comment, name='like_comment'),
    path('like-snippet/', like_snippet, name='like_snippet'),

    # CBV
    # path('notifications/', views_cbv.UserNotificationsView.as_view(), name='notifications'),
    # path('snippet/<int:id>/', views_cbv.SnippetDetailView.as_view(), name='snippet-detail'),
    # path('snippet/<int:pk>/delete/', views_cbv.SnippetDeleteView.as_view(), name='snippet-delete'),
    # path('logout/', views_cbv.LogoutView.as_view(next_page='MainApp:home'), name='custom_logout'),

    # subscribe
    path('subscribe/<int:author_id>/', subscribe_author, name='subscribe_author'),
    path('unsubscribe/<int:author_id>/', unsubscribe_author, name='unsubscribe_author'),
]
