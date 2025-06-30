from django.db import models


class Snippet(models.Model):
    LANG_CHOICES = [
        ('-', '--- выберите ---'),
        ('python', 'Python'),
        ('cpp', 'C++'),
        ('java', 'Java'),
        ('js', 'JavaScript'),
    ]

    name = models.CharField(max_length=100)
    lang = models.CharField(max_length=30, choices=LANG_CHOICES, default='-')
    code = models.TextField(max_length=5000)
    creation_date = models.DateTimeField(auto_now=True)
