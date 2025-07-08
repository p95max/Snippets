from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from MainApp.models import Snippet, LANG_CHOICES, Comment


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description', 'public']
        labels = {
            'name': 'Название сниппета',
            'lang': 'Язык программирования',
            'code': 'Код',
            'description': 'Описание',
            'is_public': 'Публичный сниппет',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'lang': forms.Select(attrs={'class': 'form-control'}, choices=LANG_CHOICES),
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите код'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание (опционально)'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Имя слишком короткое (должно быть минимум 3 символа)')
        return name


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(label='Ваш Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Ваш логин',
            'email': 'Ваш Email',
        }
        help_texts = {
            'username': 'Только буквы, цифры и символы @/./+/-/_',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Введите пароль'
        self.fields['password1'].help_text = 'Пароль должен содержать минимум 8 символов и не быть слишком простым.'
        self.fields['password2'].label = 'Введите пароль ещё раз'
        self.fields['password2'].help_text = 'Введите тот же пароль ещё раз для подтверждения.'

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if not pass1 or not pass2 or pass1 != pass2:
            raise forms.ValidationError('Пароли не совпадают либо пустые')
        return pass2


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'placeholder': 'Ваш комментарий',
                'class': 'form-control',
                'rows': 3,
            }),
        }
        labels = {
            'text': '',
        }


class SnippetSearchForm(forms.Form):
    query = forms.CharField(
        label='Поиск',
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Поиск по названию, коду или языку...'})
    )
