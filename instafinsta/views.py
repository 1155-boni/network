from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from .models import Profile, Post, Message
from django.db.models import Q, Max
from .forms import ProfileForm, MessageForm
from django.db.models import Count



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
    user = request.user

    # Get all threads (sender or receiver = current user)
    threads = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user))
        .values("sender", "receiver")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    conversations = []
    for t in threads:
        other_id = t["receiver"] if t["sender"] == user.id else t["sender"]

        # Get the actual user object
        other_user = User.objects.get(id=other_id)

        # Count unread messages from this user
        unread_count = Message.objects.filter(
            sender_id=other_id, receiver=user, is_read=False
        ).count()

        # Get latest message between the two
        last_message = (
            Message.objects.filter(
                Q(sender_id=other_id, receiver=user) | 
                Q(sender=user, receiver_id=other_id)
            )
            .order_by("-timestamp")
            .first()
        )

        conversations.append({
            "user": other_user,            # pass full user object
            "last_message": last_message,
            "unread_count": unread_count,
        })

    return render(request, "messages/inbox.html", {"conversations": conversations})
@login_required
def message_thread(request, user_id):
    receiver = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        sender__in=[request.user, receiver],
        receiver__in=[request.user, receiver]
    ).order_by("timestamp")

    # Mark unread messages as read
    Message.objects.filter(sender=receiver, receiver=request.user, is_read=False).update(is_read=True)

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.sender = request.user
            msg.receiver = receiver
            msg.save()
            return redirect("messages_with", user_id=receiver.id)
    else:
        form = MessageForm()

    users = User.objects.exclude(id=request.user.id)
    return render(request, "messages/thread.html", {
        "receiver": receiver,
        "messages": messages,
        "form": form,
        "users": users,
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
    user = request.user

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save profile fields (bio, location, profile_pic)
            form.save()

            # Save user fields (username, email, first/last name)
            user.username = request.POST.get("username", user.username)
            user.email = request.POST.get("email", user.email)
            user.first_name = request.POST.get("first_name", user.first_name)
            user.last_name = request.POST.get("last_name", user.last_name)
            user.save()

            messages.success(request, "Profile updated successfully.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'form': form,
        'user': user,   # so template can pre-fill values
    })
@login_required
def remove_profile_pic(request):
    profile = request.user.profile
    if profile.profile_pic:  
        profile.profile_pic.delete(save=True)  # deletes file + clears DB field
    return redirect('profile')

def messages_with(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    return render(request, "messages/thread.html", {"other_user": other_user})

@login_required
def messages_list(request):
    users = User.objects.exclude(id=request.user.id).annotate(
        unread_count=Count(
            "sent_messages",
            filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False)
        )
    )
    return render(request, "messages/inbox.html", {"users": users})

