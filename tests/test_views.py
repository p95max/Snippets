import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.test import Client
from django.urls import reverse
from django.test import RequestFactory
from MainApp.views import add_snippet_page


class TestIndexPageView:
    def test_index(self):
        client = Client()
        response = client.get(reverse('MainApp:home'))

        assert response.status_code == 200
        assert response.context.get('pagename') == 'PythonBin'


@pytest.mark.django_db
class TestAddSnippetPageView:
    def setup_method(self):
        self.factory = RequestFactory()

    def test_guest_user(self):
        request = self.factory.get(reverse('MainApp:snippet-add'))
        request.user = AnonymousUser()
        response = add_snippet_page(request)

        assert response.status_code == 302


    def test_auth_user(self):
        request = self.factory.get(reverse('MainApp:snippet-add'))
        user = User.objects.create_user(username="testuser", email='test@test.com', password="testpass")
        request.user = user
        response = add_snippet_page(request)

        assert response.status_code == 200


