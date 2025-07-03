from django.contrib.auth.models import User
from django.db import models

LANG_CHOICES = [
    ('-', '--- выберите ---'),
    ('python', 'Python'),
    ('cpp', 'C++'),
    ('java', 'Java'),
    ('js', 'JavaScript'),
]
LANG_ICONS = {
    'python': 'fa-python',
    'cpp': 'fa-c++',
    'java': 'fa-java',
    'js': 'fa-javascript',
}


class Snippet(models.Model):
    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=30, choices=LANG_CHOICES, default='-')
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True, null=True)
    views_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    is_public = models.BooleanField(default=False, verbose_name='Публичный сниппет')

    def __str__(self):
        return self.name

class Comment(models.Model):
    text = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(to=User, on_delete=models.CASCADE)
    snippet = models.ForeignKey(to=Snippet, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.text} - {self.author.username}"

