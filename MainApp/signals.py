import logging
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.db.models import F
from MainApp.models import Snippet, Comment, Notification, LikeDislike, UserProfile, SubscriptionAuthor

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
        Notification.objects.create(
            recipient=instance.snippet.user,
            notification_type='comment',
            title='Комментарий',
            message=f"{instance.author.username} прокомментировал ваш сниппет",
            snippet=instance.snippet,
        )

@receiver(post_save, sender=LikeDislike)
def create_comment_like_notification(sender, instance, created, **kwargs):
    if created and isinstance(instance.content_object, Comment):
        comment = instance.content_object
        if comment.author != instance.user:
            if instance.vote == LikeDislike.LIKE:
                Notification.objects.create(
                    recipient=comment.author,
                    notification_type='like',
                    title='Ваш комментарий понравился',
                    message=f"{instance.user.username} поставил лайк ваш комментарий к сниппету '{comment.snippet.name}'",
                    snippet=comment.snippet,
                )
            elif instance.vote == LikeDislike.DISLIKE:
                Notification.objects.create(
                    recipient=comment.author,
                    notification_type='dislike',
                    title='Ваш комментарий не понравился',
                    message=f"{instance.user.username} поставил дизлайк вашему комментарию к сниппету '{comment.snippet.name}'",
                    snippet=comment.snippet,
                )

@receiver(post_save, sender=LikeDislike)
def create_snippet_like_notification(sender, instance, created, **kwargs):
    if created and isinstance(instance.content_object, Snippet):
        snippet = instance.content_object
        if snippet.user != instance.user:
            if instance.vote == LikeDislike.LIKE:
                Notification.objects.create(
                    recipient=snippet.user,
                    notification_type='like',
                    title='Ваш сниппет понравился',
                    message=f"{instance.user.username} оценил ваш сниппет '{snippet.name}'",
                    snippet=snippet,
                )
            elif instance.vote == LikeDislike.DISLIKE:
                Notification.objects.create(
                    recipient=snippet.user,
                    notification_type='dislike',
                    title='Ваш сниппет не понравился',
                    message=f"{instance.user.username} поставил дизлайк вашему сниппету '{snippet.name}'",
                    snippet=snippet,
                )

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=Snippet)
def notify_subscribers_new_snippet(sender, instance, created, **kwargs):
    if created:
        author = instance.user
        subscribers = SubscriptionAuthor.objects.filter(author=author).select_related('subscriber')
        notifications = []
        for sub in subscribers:
            if sub.subscriber == author:
                continue
            notifications.append(Notification(
                recipient=sub.subscriber,
                notification_type='follow',
                title=f'Новый сниппет от {author.username}',
                message=f'{author.username} опубликовал новый сниппет: {instance.name}',
                snippet=instance,
            ))
        Notification.objects.bulk_create(notifications)

@receiver(post_save, sender=Snippet)
def notify_subscribers_new_snippet(sender, instance, created, **kwargs):
    if created and instance.public:
        author = instance.user
        subscribers = SubscriptionAuthor.objects.filter(author=author).select_related('subscriber')
        notifications = []
        for sub in subscribers:
            notifications.append(Notification(
                recipient=sub.subscriber,
                actor=author,
                notification_type='new_snippet',
                title='Новый сниппет от автора',
                message=f'Автор {author.username} опубликовал новый сниппет: {instance.name}',
                snippet=instance,
            ))
        Notification.objects.bulk_create(notifications)