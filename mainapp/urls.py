from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from mainapp.views import index_page, add_snippet_page, snippets_page, snippet_detail

urlpatterns = [
    path('', index_page, name="home"),
    path('snippets/add', add_snippet_page, name="snippet-add"),
    path('snippets/list', snippets_page, name="snippets-list"),
    path('snippet/<int:id>', snippet_detail, name="snippet-detail"),
]