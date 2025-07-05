from mainapp.forms import SnippetSearchForm

def search_form(request):
    return {'search_form': SnippetSearchForm(request.GET)}