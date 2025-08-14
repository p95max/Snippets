from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from MainApp.models import Snippet, LANG_CHOICES, Comment, UserProfile


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description', 'tags', 'public']
        labels = {
            'name': 'Название сниппета',
            'lang': 'Язык программирования',
            'code': 'Код',
            'description': 'Описание',
            'tags': 'Теги',
            'public': 'Публичный сниппет',

        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите название'}),
            'lang': forms.Select(attrs={'class': 'form-control'}, choices=LANG_CHOICES),
            'code': forms.Textarea(attrs={'class': 'form-control', 'rows': 10, 'placeholder': 'Введите код'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Описание (опционально)'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),

        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name) < 3:
            raise forms.ValidationError('Имя слишком короткое (должно быть минимум 3 символа)')
        if len(name) > 20:
            raise forms.ValidationError('Имя слишком длинное (максимум 20 символов)')
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



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website']
        help_texts = {
            'website': 'Введите полный адрес, например: https://example.com',
        }



class SetPassword(forms.Form):
    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput,
        strip=False,
    )
    new_password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput,
        strip=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data
