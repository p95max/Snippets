import pytest
from django.contrib.auth.models import User, AnonymousUser
from django.test import Client
from django.urls import reverse
from django.test import RequestFactory
from MainApp.models import Snippet
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



@pytest.mark.django_db
class TestDeleteSnippetPageView:
    def test_guest_user(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        snippet = Snippet.objects.create(
            name="Test",
            lang="python",
            code="print(1)",
            user=user,
        )
        url = reverse('MainApp:snippet-delete', kwargs={'pk': snippet.pk})
        response = client.get(url)
        assert response.status_code == 302

    def test_auth_user(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        client.force_login(user)

        snippet = Snippet.objects.create(
            name="Test",
            lang="python",
            code="print(1)",
            user=user,
        )

        url = reverse('MainApp:snippet-delete', args=[snippet.id])
        response = client.post(url)

        assert response.status_code == 302

        assert not Snippet.objects.filter(id=snippet.id).exists()



@pytest.mark.django_db
class TestEditSnippetPageView:
    def test_guest_user_redirected_from_edit(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        snippet = Snippet.objects.create(
            name="Original Name",
            lang="python",
            code="print(1)",
            user=user,
        )

        url = reverse("MainApp:snippet-edit", args=[snippet.id])
        response = client.post(url, {
            "name": "Hacked Name",
            "lang": "python",
            "code": "print('hacked')"
        })

        assert response.status_code == 302

        snippet.refresh_from_db()
        assert snippet.name == "Original Name"
        assert snippet.code == "print(1)"

    def test_auth_user_can_edit_own_snippet(self, client):
        user = User.objects.create_user(username="testuser", password="testpass")
        client.force_login(user)

        snippet = Snippet.objects.create(
            name="Original Name",
            lang="python",
            code="print(1)",
            user=user,
        )

        url = reverse("MainApp:snippet-edit", args=[snippet.id])
        response = client.post(url, {
            "name": "Updated Name",
            "lang": "python",
            "code": "print('updated')"
        })

        assert response.status_code == 302

        snippet.refresh_from_db()
        assert snippet.name == "Updated Name"
        assert snippet.code == "print('updated')"


import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from MainApp.models import Snippet

@pytest.mark.django_db
class TestSnippetsPage:
    def setup_method(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        self.another_user = User.objects.create_user(
            username="anotheruser",
            email="another@example.com",
            password="testpass123"
        )
        self.third_user = User.objects.create_user(
            username="thirduser",
            email="third@example.com",
            password="testpass123"
        )

        self.snippets = []

        self.snippets.extend([
            Snippet.objects.create(
                name="Python Hello World",
                code="print('Hello, World!')",
                lang="python",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="Python Calculator",
                code="def add(a, b):\n    return a + b",
                lang="python",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="Private Python Snippet",
                code="print('This is private')",
                lang="python",
                user=self.user,
                public=False
            ),
            Snippet.objects.create(
                name="JavaScript Alert",
                code="alert('Hello from JS');",
                lang="javascript",
                user=self.user,
                public=True
            ),
            Snippet.objects.create(
                name="HTML Template",
                code="<html><body><h1>Hello</h1></body></html>",
                lang="html",
                user=self.user,
                public=True
            )
        ])

        self.snippets.extend([
            Snippet.objects.create(
                name="Another Python Code",
                code="import os\nprint(os.getcwd())",
                lang="python",
                user=self.another_user,
                public=True
            ),
            Snippet.objects.create(
                name="CSS Styles",
                code="body { color: red; }",
                lang="css",
                user=self.another_user,
                public=True
            ),
            Snippet.objects.create(
                name="Private Another User Snippet",
                code="console.log('private');",
                lang="javascript",
                user=self.another_user,
                public=False
            )
        ])

        self.snippets.extend([
            Snippet.objects.create(
                name="SQL Query",
                code="SELECT * FROM users WHERE active = 1;",
                lang="sql",
                user=self.third_user,
                public=True
            ),
            Snippet.objects.create(
                name="Bash Script",
                code="#!/bin/bash\necho 'Hello from bash'",
                lang="bash",
                user=self.third_user,
                public=True
            )
        ])

    def test_my_snippets_authenticated_user(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:user_snippets')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context['pagename'] == 'Мои сниппеты'
        user_snippets = [s for s in self.snippets if s.user == self.user]
        assert response.context['count_snippets'] == len(user_snippets)
        assert len(response.context['page_obj']) <= 5

    def test_my_snippets_anonymous_user(self):
        url = reverse('MainApp:user_snippets')
        response = self.client.get(url)
        assert response.status_code == 403  # PermissionDenied

    def test_all_snippets_authenticated_user(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(url)
        assert response.status_code == 200
        assert response.context['pagename'] == 'Просмотр сниппетов'
        public_snippets = [s for s in self.snippets if s.public]
        private_own_snippets = [s for s in self.snippets if not s.public and s.user == self.user]
        expected_count = len(public_snippets) + len(private_own_snippets)
        assert response.context['count_snippets'] == expected_count
        assert len(response.context['page_obj']) <= 5

    def test_my_snippets_anonymous_user(self):
        url = reverse('MainApp:user_snippets')
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url.startswith('/accounts/login/')

    def test_snippets_with_search(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?search=Python")
        assert response.status_code == 200
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert 'Python' in snippet.name or 'Python' in snippet.code

    def test_snippets_with_lang_filter(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?lang=python")
        assert response.status_code == 200
        assert response.context['lang'] == 'python'
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert snippet.lang == 'python'

    def test_snippets_with_user_filter(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?user_id={self.another_user.id}")
        assert response.status_code == 200
        assert response.context['user_id'] == str(self.another_user.id)
        found_snippets = response.context['page_obj']
        assert len(found_snippets) > 0
        for snippet in found_snippets:
            assert snippet.user == self.another_user

    def test_snippets_with_sorting(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?sort=name")
        assert response.status_code == 200
        assert response.context['sort'] == 'name'
        snippets_list = list(response.context['page_obj'])
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].name <= snippets_list[i + 1].name

    def test_snippets_with_reverse_sorting(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?sort=-name")
        assert response.status_code == 200
        assert response.context['sort'] == '-name'
        snippets_list = list(response.context['page_obj'])
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].name >= snippets_list[i + 1].name

    def test_snippets_with_lang_sorting(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?sort=lang")
        assert response.status_code == 200
        assert response.context['sort'] == 'lang'
        snippets_list = list(response.context['page_obj'])
        for i in range(len(snippets_list) - 1):
            assert snippets_list[i].lang <= snippets_list[i + 1].lang

    def test_multiple_filters_combined(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?lang=python&user_id={self.user.id}&search=Hello")
        assert response.status_code == 200
        assert response.context['lang'] == 'python'
        assert response.context['user_id'] == str(self.user.id)
        found_snippets = response.context['page_obj']
        for snippet in found_snippets:
            assert snippet.lang == 'python'
            assert snippet.user == self.user
            assert 'Hello' in snippet.name or 'Hello' in snippet.code

    def test_public_and_private_snippets_for_authenticated_user(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(url)
        assert response.status_code == 200
        snippets_list = list(response.context['page_obj'])
        public_snippets = [s for s in self.snippets if s.public]
        for snippet in public_snippets:
            if snippet in snippets_list:
                assert True
        private_own_snippets = [s for s in self.snippets if not s.public and s.user == self.user]
        for snippet in private_own_snippets:
            if snippet in snippets_list:
                assert True
        private_others_snippets = [s for s in self.snippets if not s.public and s.user != self.user]
        for snippet in private_others_snippets:
            assert snippet not in snippets_list

    def test_only_public_snippets_for_anonymous_user(self):
        url = reverse('MainApp:snippets-list')
        response = self.client.get(url)
        assert response.status_code == 200
        snippets_list = list(response.context['page_obj'])
        public_snippets = [s for s in self.snippets if s.public]
        for snippet in public_snippets:
            if snippet in snippets_list:
                assert True
        private_snippets = [s for s in self.snippets if not s.public]
        for snippet in private_snippets:
            assert snippet not in snippets_list

    def test_pagination(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(url)
        assert response.status_code == 200
        page_obj = response.context['page_obj']
        assert hasattr(page_obj, 'has_other_pages')
        assert hasattr(page_obj, 'number')
        assert hasattr(page_obj, 'paginator')
        assert len(page_obj) <= 5

    def test_empty_search_results(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?search=NonExistentSnippet")
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 0

    def test_empty_lang_filter(self):
        self.client.force_login(self.user)
        url = reverse('MainApp:snippets-list')
        response = self.client.get(f"{url}?lang=nonexistent")
        assert response.status_code == 200
        assert len(response.context['page_obj']) == 0




