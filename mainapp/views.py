from django.contrib.auth.decorators import login_required
from django.db import models
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, HttpResponseNotAllowed
from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Snippet, LANG_ICONS
from mainapp.forms import SnippetForm, UserRegistrationForm, CommentForm
from django.contrib import auth

def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'index.html', context)

def snippets_page(request):
    if request.user.is_authenticated:
        snippets = Snippet.objects.filter(Q(is_public=True) | Q(user=request.user)
        ).annotate(num_comments=Count('comment')) \
         .order_by('-creation_date')
    else:
        snippets = Snippet.objects.filter(is_public=True) \
            .annotate(num_comments=Count('comment')) \
            .order_by('-creation_date')

    for snippet in snippets:
        snippet.icon_class = get_icon_class(snippet.lang)

    return render(request, 'view_snippets.html', {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        'count_snippets': snippets.count(),
    })

def snippet_detail(request, id):
    snippet = Snippet.objects.annotate(num_comments=Count('comment')).get(id=id)
    viewed_key = f'snippet_{id}'
    comment_form = CommentForm()


    if not request.session.get(viewed_key, False):
        snippet.views_count += 1
        snippet.save(update_fields=['views_count'])
        request.session[viewed_key] = True

    context = {
        'pagename': f'Сниппет: {snippet.name}',
        'snippet': snippet,
        'comment_form': comment_form,
    }
    return render(request, 'snippet_detail.html', context)

@login_required
def user_snippet_list(request):
    snippets = Snippet.objects.filter(user=request.user) \
        .annotate(num_comments=Count('comment')) \
        .order_by('-creation_date')
    return render(request, 'user_snippets.html', {'snippets': snippets})

# Custom auth
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('mainapp:home')
        else:
            context = {
                'errors': ['Неверные логин или пароль'],
                'username': username,
            }
            return render(request, 'index.html', context)
    return redirect('mainapp:home')

def custom_logout(request):
    auth.logout(request)
    return redirect('mainapp:home')

def custom_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mainapp:home')
    else:
        form = UserRegistrationForm()

    return render(request, 'custom_auth/register.html', {'form': form})

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
            return redirect('mainapp:snippet-detail', id=snippet.pk)

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
            return redirect('mainapp:snippet-detail', id=snippet.pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, 'edit_snippet.html', {'form': form})

@login_required
def delete_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if snippet.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот сниппет.")

    if request.method == 'POST':
        snippet.delete()
        return redirect('mainapp:user_snippets')

    return redirect('mainapp:user_snippets')

# Comments
@login_required
def comment_add(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('mainapp:custom_login')

        comment_form = CommentForm(request.POST)
        snippet_id = request.POST.get('snippet_id')
        snippet = get_object_or_404(Snippet, id=snippet_id)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
            return redirect('mainapp:snippet-detail', id=snippet_id)

        return redirect('mainapp:snippet-detail', id=snippet_id)

    return HttpResponseNotAllowed(['POST'])



# UI
def get_icon_class(lang):
    return LANG_ICONS.get(lang)










