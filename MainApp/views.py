import time
from collections import defaultdict
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.decorators.http import require_POST
from MainApp.models import Snippet, Tag, Comment, Notification, LikeDislike
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm, SnippetSearchForm, UserForm, UserProfileForm, SetPassword
from django.contrib import auth
from django.shortcuts import render, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from MainApp.signals import snippet_views, snippet_deleted
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, get_user_model, login


def index_page(request):
    context = {
        'pagename': 'PythonBin',
        "auth_dropdown_open": True,}

    return render(request, 'index.html', context)

def snippets_list(request):
    pagename = 'Просмотр сниппетов'
    lang = request.GET.get('lang')
    user_id = request.GET.get('user_id')
    search = request.GET.get('search')
    sort = request.GET.get('sort', 'creation_date')

    qs = Snippet.objects.annotate(num_comments=Count('comments')).select_related('user').prefetch_related('tags')

    if user_id:
        qs = qs.filter(user_id=user_id)
    if lang:
        qs = qs.filter(lang=lang)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))

    if request.user.is_authenticated:
        qs = qs.filter(Q(public=True) | Q(user=request.user))
    else:
        qs = qs.filter(public=True)

    allowed_fields = ['name', 'lang', 'creation_date']
    if sort.startswith('-'):
        sort_field = sort[1:]
    else:
        sort_field = sort
    if sort_field not in allowed_fields:
        sort = '-creation_date'

    qs = qs.order_by(sort)

    paginator = Paginator(qs, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    active_users = User.objects.filter(snippets__public=True).distinct()

    context = {
        'pagename': pagename,
        'lang': lang,
        'user_id': user_id,
        'search': search,
        'sort': sort,
        'active_users': active_users,
        'count_snippets': qs.count(),
        'page_obj': page_obj,
        'snippets': page_obj,
    }
    return render(request, 'view_snippets.html', context)

@login_required
def my_snippets(request, per_page = 5):
    qs = Snippet.objects.filter(user=request.user)

    paginator = Paginator(qs, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'count_snippets': qs.count(),
        'sort': request.GET.get('sort', ''),
        'order': request.GET.get('order', ''),
    }
    return render(request, 'user_snippets.html', context)

def snippet_detail(request, id):
    snippet = Snippet.objects.annotate(num_comments=Count('comments')).select_related('user').get(id=id)
    viewed_key = f'snippet_{id}'
    comment_form = CommentForm()

    comments = Comment.objects.filter(snippet=snippet).order_by('-creation_date').select_related('author')
    paginator = Paginator(comments, 5)
    page_number = request.GET.get('page')
    comments_page = paginator.get_page(page_number)

    if not request.session.get(viewed_key, False):
        snippet_views.send(sender=Snippet, snippet_id=snippet.id)
        request.session[viewed_key] = True

    snippet.likes_count = snippet.likes.filter(vote=1).count()
    snippet.dislikes_count = snippet.likes.filter(vote=-1).count()
    snippet.user_like = None
    if request.user.is_authenticated:
        user_like_obj = snippet.likes.filter(user=request.user).first()
        if user_like_obj:
            snippet.user_like = user_like_obj.vote

    for comment in comments_page:
        comment.likes_count = comment.likes.filter(vote=1).count()
        comment.dislikes_count = comment.likes.filter(vote=-1).count()
        comment.user_like = None
        if request.user.is_authenticated:
            user_like_obj = comment.likes.filter(user=request.user).first()
            if user_like_obj:
                comment.user_like = user_like_obj.vote

    context = {
        'pagename': f'Сниппет: {snippet.name}',
        'snippet': snippet,
        'comment_form': comment_form,
        'comments_page': comments_page,
    }
    return render(request, 'snippet_detail.html', context=context)

def snippets_by_tag(request, tag_id):
    tag = get_object_or_404(Tag, id=tag_id)
    snippets = Snippet.objects.filter(tags__id=tag_id).order_by('-creation_date')
    paginator = Paginator(snippets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'tag': tag,
        'count_snippets': snippets.count(),
        'pagename': f'Сниппеты с тегом: {tag.name}',
    }
    return render(request, 'snippets_by_tag.html', context)

def snippets_stats(request):
    total_snippets = Snippet.objects.count()
    total_public_snippets = Snippet.objects.filter(public=True).count()
    avg_snippets_views = Snippet.objects.aggregate(avg=Avg('views_count'))['avg']
    aavg_snippets_views = round(avg_snippets_views) if avg_snippets_views else 0
    top_5_snippets = Snippet.objects.order_by('-views_count').values('id', 'name', 'views_count')[:5]
    top_3_authors = (
        User.objects
        .annotate(snippet_count=Count('snippets'))
        .filter(snippet_count__gt=0)
        .order_by('-snippet_count')[:3]
        .values('username', 'snippet_count')
    )

    context = {
        'total_snippets': total_snippets,
        'total_public_snippets': total_public_snippets,
        'avg_snippets_views': avg_snippets_views,
        'top_5_snippets': top_5_snippets,
        'top_3_authors': top_3_authors,
    }

    return render(request, 'snippets_stats.html', context=context)


# Custom auth
def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user is not None:
            if not user.check_password(password):
                messages.error(request, "Неверные логин или пароль")
                return render(request, 'index.html', {"auth_dropdown_open": True, "username": username})

            if not user.is_active:
                messages.error(request, "Аккаунт не активирован. Проверьте почту для подтверждения регистрации.")
                return render(request, 'index.html', {"auth_dropdown_open": True, "username": username})

            login(request, user)
            return redirect('MainApp:home')
        else:
            messages.error(request, "Неверные логин или пароль")
            return render(request, 'index.html', {"auth_dropdown_open": True, "username": username})
    return redirect('MainApp:home')

def custom_logout(request):
    auth.logout(request)
    return redirect('MainApp:home')

def custom_registration(request):
    if request.method == "GET":
        form = UserRegistrationForm()
        return render(request, "custom_auth/register.html", {"form": form})

    elif request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            send_activation_email(user, request)
            messages.success(request, f'Вы успешно зарегистрированы! Проверьте почту для активации аккаунта.')
            return redirect('MainApp:home')
        else:
            return render(request, "custom_auth/register.html", {"form": form})

def send_activation_email(user, request):
    """
    Отправляет email для подтверждения аккаунта
    """
    # Генерируем токен
    token = default_token_generator.make_token(user)

    # Создаем ссылку для подтверждения
    activation_url = request.build_absolute_uri(
        f'/activate/{user.id}/{token}/'
    )

    # Контекст для шаблона
    context = {
        'user': user,
        'activation_url': activation_url,
    }

    # Рендерим HTML версию письма
    html_message = render_to_string('custom_auth/account_activation.html', context)

    # Рендерим текстовую версию письма
    text_message = render_to_string('custom_auth/account_activation.txt', context)

    # Отправляем email
    send_mail(
        subject='Подтверждение аккаунта',
        message=text_message,
        html_message=html_message,
        from_email='noreply@yoursite.com',
        recipient_list=[user.email],
        fail_silently=False,
    )

    return token

def verify_activation_token(user, token):
    """
    Проверяет токен подтверждения
    """
    return default_token_generator.check_token(user, token)

def activate_account(request, user_id, token):
    """
    Подтверждение аккаунта пользователя по токену
    """
    try:
        user = User.objects.get(id=user_id)

        # Проверяем, не подтвержден ли уже аккаунт
        if user.is_active:
            messages.info(request, 'Ваш аккаунт уже подтвержден.')
            return redirect('MainApp:home')

        # Проверяем токен
        if verify_activation_token(user, token):
            user.is_active = True
            user.save()
            messages.success(request,
                             'Ваш аккаунт успешно подтвержден! Теперь вы можете войти в систему.')
            return redirect('MainApp:home')
        else:
            messages.error(request,
                           'Недействительная ссылка для подтверждения. Возможно, она устарела.')
            return redirect('MainApp:home')

    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
        return redirect('MainApp:home')

def resend_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                messages.error(request, "Этот email уже подтверждён.")
            else:
                send_activation_email(user)
                messages.success(request, "Письмо с подтверждением отправлено повторно.")
        except User.DoesNotExist:
            messages.error(request, "Пользователь с таким email не найден.")
        return redirect("MainApp:resend_email")

    return render(request, "custom_auth/resend_email.html")


# User profile
@login_required
def user_profile(request, user_id=None):
    if user_id is None or int(user_id) == request.user.id:
        user = request.user
        is_owner = True
    else:
        user = get_object_or_404(User, id=user_id)
        is_owner = False

    user_snippets = (
        Snippet.objects
        .filter(user=user)
        .select_related('user')
        .prefetch_related('tags')
    )

    user_comments = (
        Comment.objects
        .filter(author=user)
        .select_related('snippet', 'snippet__user')
    )

    snippet_actions = [
        {
            'text': 'Создал сниппет',
            'date': s.creation_date,
            'badge_class': 'bg-success',
            'badge_label': 'Сниппет',
            'url': reverse('MainApp:snippet-detail', args=[s.id]),
            'obj_name': s.name,
        }
        for s in user_snippets
    ]

    comment_actions = [
        {
            'text': 'Прокомментировал сниппет',
            'date': c.creation_date,
            'badge_class': 'bg-info',
            'badge_label': 'Комментарий',
            'url': reverse('MainApp:snippet-detail', args=[c.snippet.id]),
            'obj_name': c.snippet.name,
        }
        for c in user_comments
    ]

    like_qs = LikeDislike.objects.filter(user=user).select_related('user', 'content_type')
    content_type_to_ids = defaultdict(set)
    for like in like_qs:
        content_type_to_ids[like.content_type_id].add(like.object_id)

    id_to_obj = {}
    for ct_id, ids in content_type_to_ids.items():
        ct = ContentType.objects.get_for_id(ct_id)
        model = ct.model_class()
        # Если это Comment, делаем select_related('snippet')
        if model.__name__ == 'Comment':
            objs = model.objects.filter(id__in=ids).select_related('snippet')
        else:
            objs = model.objects.filter(id__in=ids)
        for obj in objs:
            id_to_obj[(ct_id, obj.id)] = obj

    like_actions = []
    for like in like_qs:
        obj = id_to_obj.get((like.content_type_id, like.object_id))
        if not obj:
            continue
        if hasattr(obj, 'name'):
            obj_type = 'Сниппет'
            obj_name = obj.name
            url = reverse('MainApp:snippet-detail', args=[obj.id])
        elif hasattr(obj, 'snippet'):
            obj_type = 'Комментарий'
            obj_name = obj.snippet.name
            url = reverse('MainApp:snippet-detail', args=[obj.snippet.id])
        else:
            continue

        action = {
            'text': f'{"Поставил лайк" if like.vote == 1 else "Поставил дизлайк"} к {obj_type.lower()}',
            'date': like.created_at,
            'badge_class': 'bg-warning' if like.vote == 1 else 'bg-danger',
            'badge_label': 'Лайк' if like.vote == 1 else 'Дизлайк',
            'url': url,
            'obj_name': obj_name,
            'actor_name': like.user.username,
        }
        like_actions.append(action)


    history = snippet_actions + comment_actions + like_actions
    history.sort(key=lambda x: x['date'], reverse=True)

    stats = {
        'total_snippets': user_snippets.count(),
        'avg_views': user_snippets.aggregate(avg=Avg('views_count'))['avg'] or 0,
        'top_snippets': user_snippets.order_by('-views_count').select_related('user')[:5],
    }

    notifications = (
        Notification.objects
        .filter(recipient=user)
        .select_related('snippet', 'snippet__user')
        .order_by('-created_at')[:20]
    )

    context = {
        'user': user,
        'history': history,
        'stats': stats,
        'is_owner': is_owner,
        'notifications': notifications,
    }

    return render(request, 'profile.html', context=context)

@login_required
def edit_profile(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Изменения успешно сохранены!')
            return redirect('MainApp:user_profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })

@login_required
def set_new_userpassword(request):
    if request.method == 'POST':
        form = SetPassword(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.warning(request, 'Пароль успешно изменён')
            return redirect('MainApp:user_profile')
    else:
        form = SetPassword()
    return render(request, 'set_new_pass.html', {'form': form})


#CRUD
@login_required
def add_snippet_page(request):
    form = SnippetForm(request.POST or None)

    if request.method == 'POST':
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
            return redirect('MainApp:snippet-detail', id=snippet.pk)

    context = {
        'pagename': 'Добавление нового сниппета',
        'form': form,
    }
    return render(request, 'add_snippet.html', context=context)

@login_required
def edit_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if snippet.user != request.user:
        return HttpResponseForbidden("У вас нет прав для редактирования этого сниппета.")

    if request.method == 'POST':
        form = SnippetForm(request.POST, instance=snippet)
        if form.is_valid():
            form.save()
            return redirect('MainApp:snippet-detail', id=snippet.pk)
    else:
        form = SnippetForm(instance=snippet)

    return render(request, 'edit_snippet.html', {'form': form})

@login_required
def delete_snippet_page(request, pk):
    snippet = get_object_or_404(Snippet, pk=pk)

    if snippet.user != request.user:
        return HttpResponseForbidden("Вы не можете удалить этот сниппет.")

    if request.method == 'POST':
        snippet_id = snippet.id
        snippet.delete()
        snippet_deleted.send(sender=Snippet, snippet_id=snippet_id)
        return redirect('MainApp:user_snippets')

    return redirect('MainApp:user_snippets')


# Comments
@login_required
def comment_add(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('MainApp:custom_login')

        comment_form = CommentForm(request.POST)
        snippet_id = request.POST.get('snippet_id')
        snippet = get_object_or_404(Snippet, id=snippet_id)

        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.author = request.user
            comment.snippet = snippet
            comment.save()
            return redirect('MainApp:snippet-detail', id=snippet_id)

        return redirect('MainApp:snippet-detail', id=snippet_id)

    return HttpResponseNotAllowed(['POST'])


# Notifications
@login_required
def user_notifications(request, per_page=10):
    notifications = Notification.objects.filter(
        recipient=request.user,
        notification_type__in=['comment', 'like', 'dislike'],
        snippet__isnull=False
    ).select_related('snippet', 'snippet__user').order_by('-created_at')

    paginator = Paginator(notifications, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    unread_count = Notification.objects.filter(
        recipient=request.user,
        notification_type__in=['comment', 'like', 'dislike'],
        snippet__isnull=False,
        is_read=False
    ).count()

    context = {
        'page_obj': page_obj,
        'notifications': page_obj,
        'unread_count': unread_count,
        'pagename': 'Мои уведомления',
    }
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('MainApp:notifications')

@login_required
def delete_notification(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id, recipient=request.user)
    if request.method == 'POST':
        notif.delete()
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url:
            return redirect(next_url)
    return redirect('MainApp:notifications')

@login_required
def delete_all_read_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user, is_read=True).delete()
        next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
        if next_url:
            return redirect(next_url)
    return redirect('MainApp:notifications')

@login_required
def unread_notifications_longpoll(request):
    """
    Long polling endpoint для получения количества непрочитанных уведомлений.
    Ждёт появления новых уведомлений до 20 секунд, иначе возвращает 0.
    """
    max_wait = 20
    interval = 1
    waited = 0

    initial_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    while waited < max_wait:
        current_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        if current_count > initial_count:
            return JsonResponse({
                'success': True,
                'unread_count': current_count,
                'timestamp': str(datetime.now())
            })
        time.sleep(interval)
        waited += interval

    return JsonResponse({
        'success': True,
        'unread_count': current_count,
        'timestamp': str(datetime.now())
    })


# Likes
@require_POST
def like_comment(request):
    user = request.user
    obj_id = request.POST.get('object_id')
    vote = int(request.POST.get('vote'))

    comment = Comment.objects.get(pk=obj_id)
    like_obj, created = LikeDislike.objects.get_or_create(
        user=user,
        content_type=ContentType.objects.get_for_model(Comment),
        object_id=obj_id,
        defaults={'vote': vote}
    )
    if not created:
        if like_obj.vote == vote:
            like_obj.delete()
        else:
            like_obj.vote = vote
            like_obj.save()

    likes = comment.likes.filter(vote=1).count()
    dislikes = comment.likes.filter(vote=-1).count()
    return JsonResponse(
        {
        'likes': likes,
        'dislikes': dislikes,
        'user_vote': vote if created or like_obj.vote == vote else 0
    }
    )

@require_POST
def like_snippet(request):
    user = request.user
    obj_id = request.POST.get('object_id')
    vote = int(request.POST.get('vote'))

    snippet = Snippet.objects.get(pk=obj_id)
    content_type = ContentType.objects.get_for_model(Snippet)

    like_obj, created = LikeDislike.objects.get_or_create(
        user=user,
        content_type=content_type,
        object_id=obj_id,
        defaults={'vote': vote}
    )
    if not created:
        if like_obj.vote == vote:
            like_obj.delete()
        else:
            like_obj.vote = vote
            like_obj.save()

    likes = snippet.likes.filter(vote=1).count()
    dislikes = snippet.likes.filter(vote=-1).count()
    return JsonResponse(
        {
        'likes': likes,
        'dislikes': dislikes,
        'user_vote': vote if created or like_obj.vote == vote else 0
    }
    )


# Search
def search_snippets(request):
    form = SnippetSearchForm(request.GET)
    query = ''
    snippets = Snippet.objects.none()

    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            base_q = Q(name__icontains=query) | Q(code__icontains=query) | Q(lang__icontains=query)
            if request.user.is_authenticated:
                snippets = Snippet.objects.filter(
                    (Q(public=True) | Q(user=request.user)) & base_q
                ).annotate(num_comments=Count('comment')).order_by('-creation_date')
            else:
                snippets = Snippet.objects.filter(
                    Q(public=True) & base_q
                ).annotate(num_comments=Count('comment')).order_by('-creation_date')

    paginator = Paginator(snippets, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'query': query,
        'page_obj': page_obj,
        'count_snippets': snippets.count(),
        'pagename': 'Результаты поиска',
    }

    return render(request, 'search_results.html', context=context)













