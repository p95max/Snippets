from django.urls import path
from mainapp.views import index_page, add_snippet_page, snippets_page, snippet_detail, edit_snippet_page, delete_snippet_page

app_name = 'mainapp'

urlpatterns = [
    path('', index_page, name="home"),
    path('snippets/list', snippets_page, name="snippets-list"),
    path('snippet/<int:id>', snippet_detail, name="snippet-detail"),

    path('snippets/add', add_snippet_page, name="snippet-add"),
    path('snippet/<int:pk>/edit', edit_snippet_page, name="snippet-edit"),
    path('snippet/<int:pk>/delete', delete_snippet_page, name="snippet-delete"),
]