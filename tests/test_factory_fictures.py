import pytest
from tests.factories import UserFactory, SnippetFactory, TagFactory, CommentFactory

@pytest.fixture
def user():
    return UserFactory()


# task 1
@pytest.fixture
def tag_factory():
    def _create_tags(names):
        return [TagFactory(name=name) for name in names]
    return _create_tags

@pytest.mark.django_db
def test_create_tags(tag_factory):
    tags = tag_factory(["js", "basic", "oop"])
    assert [tag.name for tag in tags] == ["js", "basic", "oop"]

# task 2
@pytest.fixture
def comment_factory():
    def _create_comments(snippet, n=1, **kwargs):
        return CommentFactory.create_batch(n, snippet=snippet, **kwargs)
    return _create_comments


@pytest.mark.django_db
def test_create_comments(comment_factory, user):
    snippet = SnippetFactory(user=user)
    comments = comment_factory(snippet=snippet, n=3, author=user)
    assert len(comments) == 3
    for comment in comments:
        assert comment.snippet == snippet
        assert comment.author == user

# task 3
@pytest.fixture
def snippets_factory():
    def _create_snippets(n=5, user=None, lang=None):
        kwargs = {}
        if user is not None:
            kwargs['user'] = user
        if lang is not None:
            kwargs['lang'] = lang
        return SnippetFactory.create_batch(n, **kwargs)
    return _create_snippets

@pytest.mark.django_db
def test_create_snippets_for_user_and_lang(snippets_factory, user):
    snippets = snippets_factory(n=2, user=user, lang="python")
    assert len(snippets) == 2
    for snippet in snippets:
        assert snippet.user == user
        assert snippet.lang == "python"