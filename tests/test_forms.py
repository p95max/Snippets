import pytest
from MainApp.forms import SnippetForm
from MainApp.models import Snippet, Tag
from django.contrib.auth.models import User

@pytest.mark.django_db
class TestSnippetForm:
    def setup_method(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.tag1 = Tag.objects.create(name="Python")
        self.tag2 = Tag.objects.create(name="Django")

    def test_valid_form(self):
        form_data = {
            'name': 'MySnippet',
            'lang': 'python',
            'code': 'print("Hello, world!")',
            'description': 'Test description',
            'tags': [self.tag1.id, self.tag2.id],
            'public': True,
        }
        form = SnippetForm(data=form_data)
        assert form.is_valid()
        snippet = form.save(commit=False)
        snippet.user = self.user
        snippet.save()
        form.save_m2m()
        assert Snippet.objects.count() == 1
        saved = Snippet.objects.first()
        assert saved.name == 'MySnippet'
        assert saved.lang == 'python'
        assert saved.public is True
        assert set(saved.tags.all()) == {self.tag1, self.tag2}

    def test_name_too_short(self):
        form_data = {
            'name': 'ab',
            'lang': 'python',
            'code': 'print(1)',
            'description': '',
            'tags': [],
            'public': False,
        }
        form = SnippetForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors
        assert 'Имя слишком короткое' in form.errors['name'][0]

    def test_name_too_long(self):
        form_data = {
            'name': 'a' * 21,
            'lang': 'python',
            'code': 'print(1)',
            'description': '',
            'tags': [],
            'public': False,
        }
        form = SnippetForm(data=form_data)
        assert not form.is_valid()
        assert 'name' in form.errors
        assert 'Имя слишком длинное' in form.errors['name'][0]