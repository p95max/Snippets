import logging
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.db.models import F
from MainApp.models import Snippet, Comment

snippet_views = Signal()
snippet_deleted = Signal()

logger = logging.getLogger(__name__)


@receiver(snippet_deleted)
def log_snippet_deleted(sender, snippet_id, **kwargs):
    logger.info(f"Сниппет с id={snippet_id} был удалён.")

@receiver(snippet_views)
def snippet_views_counter(sender, snippet_id, **kwargs):
    Snippet.objects.filter(id=snippet_id).update(views_count=F('views_count') + 1)

@receiver(post_save, sender=User)
def send_message(sender, instance, created, **kwargs):
    if created:
        print(f"--- Сигнал post_save получен ---")
        print(f"Пользователь '{instance.username}' успешно зарегистрирован!")
        print(f"Отправитель: '{sender.__name__}'")
        print(f"ID пользователя: '{instance.id}'")
        print(f"--- Конец сигнала ---")

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.snippet.user and instance.author != instance.snippet.user:
        pass