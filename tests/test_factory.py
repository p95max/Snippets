import pytest
from tests.factories import *
from MainApp.models import User

@pytest.mark.django_db
def test_task1():
    UserFactory(username='alice')
    user = User.objects.get(username='alice')

    assert user.username == 'alice'

@pytest.mark.django_db
def test_task2():
    TagFactory.create_batch(5)
    tags = Tag.objects.count()

    assert tags == 5

@pytest.mark.django_db
def test_task3():
    SnippetFactory(name='Java Quick Sort', lang='java')
    snippet = Snippet.objects.get(name='Java Quick Sort')

    assert snippet.name == 'Java Quick Sort'

@pytest.mark.django_db
def test_task4():
    tag1 = TagFactory(name="web")
    tag2 = TagFactory(name="backend")

    SnippetFactory(public=True, tags=[tag1, tag2])

    assert Tag.objects.count() == 2

@pytest.mark.django_db
def test_task5():
    user = UserFactory(username='Commenter')

    snippet = SnippetFactory(public=True, name="My First Snippet")

    comment = CommentFactory(snippet=snippet, author=user)

    assert comment.snippet == snippet
    assert comment.author == user
    assert user.username == 'Commenter'

@pytest.mark.django_db
def test_task6():
    user = UserFactory()

    snippets = SnippetFactory.create_batch(3, user=user, public=False)

    assert len(snippets) == 3
    for snippet in snippets:
        assert snippet.user == user
        assert snippet.public == False

@pytest.mark.django_db
def test_task7():
    user1 = UserFactory.create()
    user2 = UserFactory.create()
    user3 = UserFactory.create()

    snippet = SnippetFactory(public=True, user=user1)

    comment1 = CommentFactory(snippet=snippet, author=user1)
    comment2 = CommentFactory(snippet=snippet, author=user2)

    assert comment1.snippet == snippet
    assert comment2.snippet == snippet
    assert comment1.author == user1
    assert comment2.author == user2
    assert snippet.user == user1
    assert snippet.public == True

@pytest.mark.django_db
def test_task8():
    user1 = UserFactory()
    user2 = UserFactory()

    snippets = SnippetFactory.create_batch(10, public=False)

    for snippet in snippets:
        CommentFactory.create_batch(5, snippet=snippet, author=user1)
        CommentFactory.create_batch(5, snippet=snippet, author=user2)

        authors = list(snippet.comment_set.values_list('author', flat=True))
        assert authors.count(user1.id) == 5
        assert authors.count(user2.id) == 5
        assert len(snippets) == 10









