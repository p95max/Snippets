from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from MainApp.models import Snippet, Tag, Comment
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm, SnippetSearchForm
from django.contrib import auth
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from MainApp.signals import snippet_views, snippet_deleted
from django.contrib import messages


def index_page(request):
    context = {'pagename': 'PythonBin'}

    messages.success(request, 'Добро пожаловать на сайт!')
    messages.info(request, 'Добро пожаловать на сайт!')
    messages.warning(request, 'Добро пожаловать на сайт!')

    return render(request, 'index.html', context)


def snippets_list(request):
    print(f"[DEBUG] snippets_list called, user={request.user}")
    pagename = 'Просмотр сниппетов'
    lang = request.GET.get('lang')
    user_id = request.GET.get('user_id')
    search = request.GET.get('search')
    sort = request.GET.get('sort', 'creation_date')

    qs = Snippet.objects.annotate(num_comments=Count('comment'))

    if user_id:
        qs = qs.filter(user_id=user_id)
    if lang:
        qs = qs.filter(lang=lang)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))

    # Показываем только публичные или свои сниппеты
    if request.user.is_authenticated:
        qs = qs.filter(Q(public=True) | Q(user=request.user))
    else:
        qs = qs.filter(public=True)

    # Сортировка
    allowed_fields = ['name', 'lang', 'creation_date']
    if sort.startswith('-'):
        sort_field = sort[1:]
    else:
        sort_field = sort
    if sort_field not in allowed_fields:
        sort = '-creation_date'  # сортировка по умолчанию

    qs = qs.order_by(sort)

    # Пагинация
    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    active_users = User.objects.filter(snippet__public=True).distinct()

    context = {
        'pagename': pagename,
        'lang': lang,
        'user_id': user_id,
        'search': search,
        'sort': sort,
        'active_users': active_users,
        'count_snippets': qs.count(),
        'page_obj': page_obj,
        'snippets': page_obj,
    }
    return render(request, 'view_snippets.html', context)

@login_required
def my_snippets(request, per_page = 5):
    qs = Snippet.objects.filter(user=request.user)

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'count_snippets': qs.count(),
        'sort': request.GET.get('sort', ''),
        'order': request.GET.get('order', ''),
    }
    return render(request, 'user_snippets.html', context)



def snippet_detail(request, id):
    snippet = Snippet.objects.annotate(num_comments=Count('comment')).get(id=id)
    viewed_key = f'snippet_{id}'
    comment_form = CommentForm()

    # Пагинация
    comments = Comment.objects.filter(snippet=snippet).order_by('-creation_date')
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    comments_page = paginator.get_page(page_number)
    # Счётчик количества просмотров через сигналы
    if not request.session.get(viewed_key, False):
        snippet_views.send(sender=Snippet, snippet_id=snippet.id)
        request.session[viewed_key] = True

    context = {
        'pagename': f'Сниппет: {snippet.name}',
        'snippet': snippet,
        'comment_form': comment_form,
        'comments_page': comments_page,
    }
    return render(request, 'snippet_detail.html', context=context)

def snippets_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    snippets = Snippet.objects.filter(tags__id=tag_id).order_by('-creation_date')
    paginator = Paginator(snippets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'tag': tag,
        'count_snippets': snippets.count(),
        'pagename': f'Сниппеты с тегом: {tag.name}',
    }
    return render(request, 'snippets_by_tag.html', context)

def snippets_stats(request):
    total_snippets = Snippet.objects.count()
    total_public_snippets = Snippet.objects.filter(public=True).count()
    avg_snippets_views = Snippet.objects.aggregate(avg=Avg('views_count'))['avg']
    aavg_snippets_views = round(avg_snippets_views)
    top_5_snippets = Snippet.objects.order_by('-views_count').values('id', 'name', 'views_count')[:5]
    top_3_authors = (
        User.objects
        .annotate(snippet_count=Count('snippet'))
        .filter(snippet_count__gt=0)
        .order_by('-snippet_count')[:3]
        .values('username', 'snippet_count')
    )

    context = {
        'total_snippets': total_snippets,
        'total_public_snippets': total_public_snippets,
        'avg_snippets_views': avg_snippets_views,
        'top_5_snippets': top_5_snippets,
        'top_3_authors': top_3_authors,
    }

    return render(request, 'snippets_stats.html', context=context)


# Custom auth
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('MainApp:home')
        else:
            context = {
                'errors': ['Неверные логин или пароль'],
                'username': username,
            }
            return render(request, 'index.html', context)
    return redirect('MainApp:home')

def custom_logout(request):
    auth.logout(request)
    return redirect('MainApp:home')



def custom_registration(request):
    if request.method == "GET":
        form = UserRegistrationForm()
        return render(request, "custom_auth/register.html", {"form": form})

    elif request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  #
            messages.success(request, f'Добро пожаловать, {user.username}! Вы успешно зарегистрированы.')
            return redirect('MainApp:home')
        else:
            return render(request, "custom_auth/register.html", {"form": form})

#CRUD
@login_required
def add_snippet_page(request):
    form = SnippetForm(request.POST or None)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
            return redirect('MainApp:snippet-detail', id=snippet.pk)

    context = {
        'pagename': 'Добавление нового сниппета',
        'form': form,
    }
    return render(request, 'add_snippet.html', context=context)

@login_required
def edit_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if snippet.user != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого сниппета.")

    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('MainApp:snippet-detail', id=snippet.pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, 'edit_snippet.html', {'form': form})

@login_required
def delete_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if snippet.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот сниппет.")

    if request.method == 'POST':
        snippet_id = snippet.id
        snippet.delete()
        snippet_deleted.send(sender=Snippet, snippet_id=snippet_id)
        return redirect('MainApp:user_snippets')

    return redirect('MainApp:user_snippets')

# Comments
@login_required
def comment_add(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('MainApp:custom_login')

        comment_form = CommentForm(request.POST)
        snippet_id = request.POST.get('snippet_id')
        snippet = get_object_or_404(Snippet, id=snippet_id)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
            return redirect('MainApp:snippet-detail', id=snippet_id)

        return redirect('MainApp:snippet-detail', id=snippet_id)

    return HttpResponseNotAllowed(['POST'])

def search_snippets(request):
    form = SnippetSearchForm(request.GET)
    query = ''
    snippets = Snippet.objects.none()

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            base_q = Q(name__icontains=query) | Q(code__icontains=query) | Q(lang__icontains=query)
            if request.user.is_authenticated:
                snippets = Snippet.objects.filter(
                    (Q(public=True) | Q(user=request.user)) & base_q
                ).annotate(num_comments=Count('comment')).order_by('-creation_date')
            else:
                snippets = Snippet.objects.filter(
                    Q(public=True) & base_q
                ).annotate(num_comments=Count('comment')).order_by('-creation_date')

    paginator = Paginator(snippets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'page_obj': page_obj,
        'count_snippets': snippets.count(),
        'pagename': 'Результаты поиска',
    }

    return render(request, 'search_results.html', context=context)











