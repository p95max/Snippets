from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from mainapp.models import Snippet, LANG_CHOICES


class SnippetForm(forms.ModelForm):
    class Meta:
        model = Snippet
        fields = ['name', 'lang', 'code', 'description', 'is_public']
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
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        pass1 = self.cleaned_data.get('password1')
        pass2 = self.cleaned_data.get('password2')
        if not pass1 or not pass2 or pass1 != pass2:
            raise forms.ValidationError('Пароли не совпадают либо пустые')
        return pass2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user