import pytest
import pytest
from django.contrib.auth.models import User
from django.db import transaction

from MainApp.models import Snippet, Comment, Tag
from MainApp.models import Tag


@pytest.mark.django_db
class TestTagModel:
    """Тесты для модели Tag"""

    def test_tag_creation(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name="Python")
        assert tag.name == "Python"

        assert Tag.objects.count() == 1

    def test_duplicate_tag_names_not_allowed(self):
        """Тест, что теги с одинаковыми именами недопустимы"""
        from django.db import IntegrityError

        tag1 = Tag.objects.create(name="Python")

        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Tag.objects.create(name="Python")

        assert Tag.objects.filter(name="Python").count() == 1
        assert Tag.objects.get(name="Python") == tag1




@pytest.mark.django_db
class TestCommentModel:
    """Тесты для модели Comment"""

    def test_comment_creation(self):
        """Тест создания комментария"""
        user = User.objects.create_user(username="testuser", password="testpass")
        tag = Tag.objects.create(name="Python")
        snippet = Snippet.objects.create(
            name="Test Snippet",
            lang="python",
            code="print('Hello, world!')",
            user=user,
        )
        snippet.tags.add(tag)

        comment = Comment.objects.create(
            text="Отличный сниппет!",
            author=user,
            snippet=snippet,
        )

        assert Comment.objects.count() == 1
        saved_comment = Comment.objects.first()
        assert saved_comment.text == "Отличный сниппет!"
        assert saved_comment.author == user
        assert saved_comment.snippet == snippet