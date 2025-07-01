from django.shortcuts import render, redirect, get_object_or_404
from mainapp.models import Snippet, LANG_ICONS
from mainapp.forms import SnippetForm


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'index.html', context)

def snippets_page(request):
    snippets = Snippet.objects.all().order_by('-creation_date')

    for snippet in snippets:
        snippet.icon_class = get_icon_class(snippet.lang)

    count_snippets = snippets.count()
    context = {
        'pagename': 'Просмотр сниппетов',
        'snippets': snippets,
        'count_snippets': count_snippets,
    }
    return render(request, 'view_snippets.html', context)

def snippet_detail(request, id):
    snippet = get_object_or_404(Snippet, id=id)
    viewed_key = f'snippet_{id}'

    if not request.session.get(viewed_key, False):
        snippet.views_count += 1
        snippet.save(update_fields=['views_count'])
        request.session[viewed_key] = True

    context = {
        'pagename': f'Сниппет: {snippet.name}',
        'snippet': snippet
    }
    return render(request, 'snippet_detail.html', context)

def get_icon_class(lang):
    return LANG_ICONS.get(lang)

#CRUD
def add_snippet_page(request):
    form = SnippetForm(request.POST or None)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save()
            return redirect('mainapp:snippet-detail', id=snippet.pk)

    context = {
        'pagename': 'Добавление нового сниппета',
        'form': form,
    }
    return render(request, 'add_snippet.html', context=context)

def edit_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('mainapp:snippet-detail', id=snippet.pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, 'edit_snippet.html', {'form': form})

def delete_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if request.method == 'POST':
        snippet.delete()
        return redirect('mainapp:snippets-list')
    return redirect('mainapp:snippets-list')









