from django import forms
from mainapp.models import Snippet


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code']
        labels = {
            'name': 'Название сниппета',
            'lang': 'Язык программирования',
            'code': 'Код',
        }

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'lang': forms.Select(attrs={'class': 'form-control'}),
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите код'}),
        }