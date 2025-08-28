from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Profile, Post, Message
from django.db.models import Q
from .forms import ProfileForm, MessageForm


# ---------------------------
# Auth Views
# ---------------------------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto login after signup
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('feed')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')

# ---------------------------
# Profile View
# ---------------------------
@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        # profile picture update
        if 'profile_pic' in request.FILES:
            profile.profile_pic = request.FILES['profile_pic']
            profile.save()
            return redirect('profile')

    return render(request, 'profile.html', {'profile': profile})

# ---------------------------
# Posts
# ---------------------------
@login_required
def create_post(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        caption = request.POST.get('caption')
        image = request.FILES.get('image')
        Post.objects.create(user=request.user, content=content, caption=caption, image=image)
        return redirect('feed')
    return render(request, 'create_post.html')


@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'feed.html', {'posts': posts})

# ---------------------------
# Messaging
# ---------------------------

@login_required
def inbox(request):
    """Show all users you have conversations with."""
    users = User.objects.exclude(id=request.user.id)
    return render(request, "messages/inbox.html", {"users": users})


@login_required
def message_thread(request, user_id):
    """Show conversation with a specific user."""
    other_user = get_object_or_404(User, id=user_id)

    # Get all messages between the two users
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by("timestamp")

    # Mark messages as read
    Message.objects.filter(receiver=request.user, sender=other_user, is_read=False).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = other_user
            msg.save()
            return redirect("message_thread", user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, "messages/thread.html", {
        "other_user": other_user,
        "messages": messages,
        "form": form,
    })


# ---------------------------
# Home (redirect to feed or login)
# ---------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return redirect('login')

@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'edit_profile.html', {'form': form})

@login_required
def remove_profile_pic(request):
    profile = request.user.profile
    if profile.profile_pic:  
        profile.profile_pic.delete(save=True)  # deletes file + clears DB field
    return redirect('profile')