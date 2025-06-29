from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import Profile
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import Post, Comment, like, Follow
from .forms import CommentForm, ProfileForm
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count

class HomeView(LoginRequiredMixin, View):
    login_url = 'login'  # or your login URL name

from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings

@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user
    posts = Post.objects.filter(user=user).order_by('-created_at')
    return render(request, 'main/profile.html', {
        'user': user,
        'posts': posts,
    })

from django.contrib.auth.views import redirect_to_login

def login_redirect(request):
    next_url = request.get_full_path()
    if url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return redirect_to_login(next_url)
    return redirect_to_login('/')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_by_username', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'main/edit_profile.html', {'form': form})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Your post has been created successfully!')
            return redirect('profile_by_username', username=request.user.username)
    else:
        form = PostForm()
    return render(request, 'main/create_post.html', {'form': form})

@login_required
def post_detail(request, post_id):
    from django.shortcuts import get_object_or_404
    post = get_object_or_404(Post, id=post_id)
    comments = post.comment_set.all()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            messages.success(request, 'You commented!')
            return redirect('post_detail', post_id=post.id)
    else:
        comment_form = CommentForm()
    return render(request, 'main/post_detail.html', {'post': post, 'comments': comments, 'comment_form': comment_form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your account has been created successfully!')
            return redirect('login')
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = RegisterForm()
    return render(request, 'main/signup.html', {'form': form})


@login_required(login_url='login')  # or your login URL name
def home(request):
    if request.user.is_authenticated:
        following= Follow.objects.filter(follower=request.user).values_list('following', flat=True)
        user_likes = set(like.objects.filter(user=request.user).values_list('post_id', flat=True))
        user_comments = set(Comment.objects.filter(user=request.user).values_list('post_id', flat=True))
    else:
        following = []
        user_likes = set()
        user_comments = set()
    posts = Post.objects.annotate(
        like_count=Count('likes')
    ).order_by('-created_at')
    for post in posts:
        post.liked_by_user = post.id in user_likes
        post.commented_by_user = post.id in user_comments
    # Check if there's a commented post ID in the request
    if request.method == "POST":
        commented_post_id = request.POST.get('post_id')
    else:
        commented_post_id = None

    return render(request, 'main/home.html', {
        'posts': posts,
        'commented_post_id': commented_post_id,
    })


from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User

# Create your views here.

from django.http import JsonResponse

@login_required
def like_post(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        if request.method == 'GET':
            return redirect('home')
        else:
            return JsonResponse({'error': 'Post not found'}, status=404)
    if request.method == 'POST':
        user = request.user
        existing_like = like.objects.filter(user=user, post=post)
        if existing_like.exists():
            existing_like.delete()
            liked = False
        else:
            like.objects.create(user=user, post=post)
            liked = True
        like_count = like.objects.filter(post=post).count()
        return JsonResponse({'liked': liked, 'like_count': like_count})
    elif request.method == 'GET':
        # Redirect to home on GET to match test expectations
        return redirect('home')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def comment_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        content = request.POST.get('content')
        if content:
            comment = Comment.objects.create(user=request.user, post=post, content=content)
            comment_data = {
                'user': comment.user.username,
                'content': comment.content,
                'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            }
            return JsonResponse({'success': True, 'comment': comment_data})
        else:
            return JsonResponse({'success': False, 'error': 'Content is required.'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    following = Follow.objects.filter(follower=request.user).values_list('following', flat=True)
    return render(request, 'main/user_list.html', {'users': users, 'following': following})

from django.http import JsonResponse

@login_required
def follow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        if target_user == request.user:
            # Prevent following self
            return redirect('profile_by_username', username=request.user.username)
        Follow.objects.get_or_create(follower=request.user, following=target_user)
        # Always redirect to profile_by_username to match tests
        return redirect('profile_by_username', username=target_user.username)
    return redirect('profile_by_username', username=request.user.username)

@login_required
def unfollow_user(request, user_id):
    if request.method == "POST":
        target_user = get_object_or_404(User, id=user_id)
        Follow.objects.filter(follower=request.user, following=target_user).delete()
        # Always redirect to profile_by_username to match tests
        return redirect('profile_by_username', username=target_user.username)
    return redirect('profile_by_username', username=request.user.username)

def custom_logout(request):
    logout(request)
    return render(request, 'main/logout.html')

from django.shortcuts import redirect

@login_required
def user_messages(request):
    """
    Redirect to chats page to avoid missing template error.
    """
    to_user = request.GET.get('to', '')
    url = '/chats/'
    if to_user:
        url += f'?to={to_user}'
    return redirect(url)

def some_view(request):
    if not request.user.is_authenticated:
        messages.info(request, "Please login first to see posts.")
        return redirect('login')

@login_required
@login_required
def chats(request):
    from .models import Message  # Import here to avoid circular import
    to_username = request.GET.get('to')
    active_friend = None
    messages = []
    # Fetch friends as users that the current user is following
    friends = User.objects.filter(followers__follower=request.user)

    if to_username:
        active_friend = get_object_or_404(User, username=to_username)
        # Fetch messages between the logged-in user and the active friend
        messages = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=active_friend)) |
            (Q(sender=active_friend) & Q(receiver=request.user))
        ).order_by('created_at')
    else:
        # Optionally, show the most recent chat or leave blank
        if friends.exists():
            active_friend = friends.first()
            messages = Message.objects.filter(
                (Q(sender=request.user) & Q(receiver=active_friend)) |
                (Q(sender=active_friend) & Q(receiver=request.user))
            ).order_by('created_at')

    return render(request, 'main/chats.html', {
        'friends': friends,
        'active_friend': active_friend,
        'messages': messages,
        'user': request.user,
    })
def search(request):
    query = request.GET.get('q', '')
    posts = []
    users = []
    if query:
        posts = Post.objects.filter(caption__icontains=query)
        users = User.objects.filter(username__icontains=query)
    return render(request, 'main/home.html', {
        'posts': posts,
        'users': users,
        'query': query
    })

@login_required
def chat_room(request, username):
    from .models import Message
    active_friend = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=active_friend)) |
        (Q(sender=active_friend) & Q(receiver=request.user))
    ).order_by('created_at')
    friends = User.objects.exclude(id=request.user.id)
    return render(request, 'main/chats.html', {
        'friends': friends,
        'active_friend': active_friend,
        'messages': messages,
        'user': request.user,
        'active_id': active_friend.id,
    })

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Message

@login_required
def chat_send_message(request):
    if request.method == 'POST' and request.user.is_authenticated:
        to_username = request.POST.get('to_username')
        text = request.POST.get('text', '').strip()
        image = request.FILES.get('image', None)
        if not to_username or (not text and not image):
            return JsonResponse({'success': False, 'error': 'Missing recipient or message content.'})
        receiver = get_object_or_404(User, username=to_username)
        message = Message(sender=request.user, receiver=receiver, text=text)
        if image:
            message.image = image
        message.save()
        message_data = {
            'id': message.id,
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'text': message.text,
            'image_url': message.image.url if message.image else '',
            'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse({'success': True, 'message': message_data})
    return JsonResponse({'success': False, 'error': 'Invalid request method or not authenticated.'})
