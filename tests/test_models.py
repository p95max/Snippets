import pytest
from django.db import IntegrityError

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

        # Создаем первый тег
        tag1 = Tag.objects.create(name="Python")

        # Пытаемся создать второй тег с тем же именем
        # Должно возникнуть исключение IntegrityError
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Python")

    @pytest.mark.django_db
    def test_tag_count_after_duplicate_attempt(self):
        Tag.objects.create(name="Python")
        assert Tag.objects.filter(name="Python").count() == 1