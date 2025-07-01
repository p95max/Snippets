from django import forms
from mainapp.models import Snippet, LANG_CHOICES


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description']
        labels = {
            'name': 'Название сниппета',
            'lang': 'Язык программирования',
            'code': 'Код',
            'description': 'Описание'
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'lang': forms.Select(attrs={'class': 'form-control'}, choices=LANG_CHOICES),
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите код'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание (опционально)'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Имя слишком короткое(должно быть минимум 3 символа)')
        return name
