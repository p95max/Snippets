import factory
from django.contrib.auth.models import User
from MainApp.models import Snippet, Comment, Tag


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User  # Указываем, какую модель будет создавать эта фабрика
        django_get_or_create = ('username',)  # Опционально: предотвращает создание дубликатов по username

    username = factory.Sequence(lambda n: f'user_{n}')  # Генерирует user_0, user_1 и т.д.
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')  # Зависит от других полей
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')  # Для хеширования пароля



class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: f'tag_{n}')



class SnippetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Snippet

    name = factory.Sequence(lambda n: f'snippet_{n}')
    lang = factory.Iterator(['python', 'cpp', 'java', 'javascript'])
    code = factory.Faker('text', max_nb_chars=1000)
    views_count = factory.Faker('random_int', min=0, max=1000)
    public = factory.Faker('boolean')
    user = factory.SubFactory(UserFactory)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            # Если переданы теги, используем их
            for tag in extracted:
                self.tags.add(tag)
        else:
            # Иначе создаем случайные теги
            import random
            num_tags = random.randint(1, 3)
            tags = TagFactory.create_batch(num_tags)
            for tag in tags:
                self.tags.add(tag)



class CommentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Comment

    text = factory.Faker('text', max_nb_chars=500)
    author = factory.SubFactory(UserFactory)
    snippet = factory.SubFactory(SnippetFactory)