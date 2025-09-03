import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from django.contrib import messages
from instafinsta.serializers import ProfileDetailSerializer, ProfileSerializer, ProfileUpdateSerializer
from .models import Profile, Post, Comment, Message
from .forms import ProfileForm, MessageForm, UserForm, UserUpdateForm
from django.db.models import Q, Max, Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes
from rest_framework.pagination import PageNumberPagination

# ---------------------------
# Auth Views
# ---------------------------
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Auto login after signup
            return redirect('feed')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get("next") or request.GET.get("next")
            return redirect(next_url) if next_url else redirect("feed")  # Fallback to feed
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {
        "form": form,
        "next": request.GET.get("next", "")
    })

def logout_view(request):
    logout(request)
    return redirect('login')

# ---------------------------
# Profile Views
# ---------------------------
@login_required
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
    else:
        user = request.user

    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(author=user).order_by("-created_at")
    is_owner = (user == request.user)
    followers_count = profile.followers.count()
    following_count = profile.following.count()

    return render(request, "profile.html", {
        "profile": profile,
        "posts": posts,
        "is_owner": is_owner,
        "followers_count": followers_count,
        "following_count": following_count,
    })

@login_required
def edit_profile(request):
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("profile", username=request.user.username)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, "edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
    })

@api_view(['GET', 'POST'])
@parser_classes([MultiPartParser, FormParser])
def avatar(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)
    serializers = ProfileUpdateSerializer(instance=profile, data=request.data)
    if request.method == 'POST':
        image = request.FILES.get('image')
        if not image:
            return Response(serializers.errors, status=400)
        profile.avatar = image
        profile.save()
        return Response({
            "message": "Image uploaded successfully",
            "avatar": profile.avatar.url
        }, status=201)
    if request.method == 'GET':
        return Response(serializers.data, status=200)
    



@login_required
def remove_profile_pic(request):
    profile = request.user.profile
    if profile.avatar:  # Use 'avatar' to match CloudinaryField
        profile.avatar.delete(save=True)  # Deletes file from Cloudinary and clears DB field
    return redirect('profile')

# ---------------------------
# Posts Views
# ---------------------------
@login_required
def create_post(request):
    if request.method == "POST":
        caption = request.POST.get("caption")
        content = request.POST.get("content")
        image = request.FILES.get("image")

        Post.objects.create(
            author=request.user,  # Changed from 'user' to 'author' to match model
            caption=caption,
            content=content,
            image=image
        )
        return redirect("feed")

    return render(request, "create_post.html")

@login_required
def feed(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'feed.html', {'posts': posts})

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, author=request.user)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect("feed")

@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)  # Unlike
    else:
        post.likes.add(request.user)  # Like
    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        content = request.POST.get("content")
        if content.strip():
            Comment.objects.create(post=post, user=request.user, content=content)
    return redirect(request.META.get("HTTP_REFERER", "feed"))

@login_required
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, "post_detail.html", {"post": post})

# ---------------------------
# Messaging Views
# ---------------------------
@login_required
def inbox(request):
    user = request.user
    threads = (
        Message.objects.filter(Q(sender=user) | Q(receiver=user))
        .values("sender", "receiver")
        .annotate(last_msg=Max("timestamp"))
        .order_by("-last_msg")
    )

    conversations = []
    for t in threads:
        other_id = t["receiver"] if t["sender"] == user.id else t["sender"]
        other_user = User.objects.get(id=other_id)
        unread_count = Message.objects.filter(
            sender_id=other_id, receiver=user, is_read=False
        ).count()
        last_message = (
            Message.objects.filter(
                Q(sender_id=other_id, receiver=user) | Q(sender=user, receiver_id=other_id)
            )
            .order_by("-timestamp")
            .first()
        )
        conversations.append({
            "user": other_user,
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
            return redirect("message_thread", user_id=receiver.id)
    else:
        form = MessageForm()

    return render(request, "messages/thread.html", {
        "receiver": receiver,
        "messages": messages,
        "form": form,
    })

@login_required
def messages_with(request, user_id=None):
    profile = request.user.profile

    # Get only people the user is following
    following_profiles = profile.following.all()
    following_users = User.objects.filter(profile__in=following_profiles)

    receiver = None
    messages = None
    form = MessageForm()

    if user_id:
        receiver = get_object_or_404(User, id=user_id)
        messages = Message.objects.filter(
            sender__in=[request.user, receiver],
            receiver__in=[request.user, receiver]
        ).order_by("timestamp")

        if request.method == "POST":
            form = MessageForm(request.POST)
            if form.is_valid():
                msg = form.save(commit=False)
                msg.sender = request.user
                msg.receiver = receiver
                msg.save()
                return redirect("messages_with", user_id=receiver.id)

    return render(request, "messages/thread.html", {
        "users": following_users,  # 👈 only show following
        "receiver": receiver,
        "messages": messages,
        "form": form,
    })
@login_required
def messages_list(request):
    users = User.objects.filter(
        profile__followers=request.user
    ).exclude(id=request.user.id).annotate(
        unread_count=Count(
            "sent_messages",
            filter=Q(sent_messages__receiver=request.user, sent_messages__is_read=False)
        )
    )
    return render(request, "messages/inbox.html", {"users": users})

# ---------------------------
# Explore View
# ---------------------------
@login_required
def explore(request):
    query = request.GET.get("q", "")

    if query:
        users = User.objects.filter(username__icontains=query).exclude(id=request.user.id)
        posts = []
    else:
        users = []
        posts = list(Post.objects.exclude(author=request.user))
        random.shuffle(posts)

    return render(request, "explore.html", {
        "users": users,
        "posts": posts,
        "query": query,
    })

# ---------------------------
# View Profile
# ---------------------------

@login_required
def view_profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user_profile)
    is_owner = (request.user == user_profile)
    followers_count = profile.followers.count()
    following_count = profile.following.count()
    posts = Post.objects.filter(author=user_profile).order_by("-created_at")

    if request.method == "POST" and is_owner:
        if "avatar" in request.FILES:  # Legacy field name, adjust if needed
            profile.avatar = request.FILES["avatar"]  # Use 'avatar' to match CloudinaryField
            profile.save()
            messages.success(request, "Profile picture updated successfully!")
            return redirect("view_profile", username=username)

    return render(request, "view_profile.html", {
        "user_profile": user_profile,
        "profile": profile,
        "posts": posts,
        "is_owner": is_owner,
        "followers_count": followers_count,
        "following_count": following_count,
    })

# ---------------------------
# Follow/Unfollow Views
# ---------------------------
@login_required
def follow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    if request.user == target_user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect("view_profile", username=username)

    if request.user in target_profile.followers.all():
        target_profile.followers.remove(request.user)
        messages.success(request, f"You unfollowed {target_user.username}.")
    else:
        target_profile.followers.add(request.user)
        messages.success(request, f"You followed {target_user.username}.")

    return redirect("view_profile", username=username)


@login_required
def unfollow_toggle(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    if request.user == target_user:
        messages.warning(request, "You cannot unfollow yourself.")
        return redirect("view_profile", username=username)
    
    if request.user in target_profile.followers.all():
        target_profile.followers.remove(request.user)
        messages.success(request, f"You unfollowed {target_user.username}.")
    else:
        target_profile.followers.add(request.user)
        messages.success(request, f"You followed {target_user.username}.")

        return redirect("view_profile", username=username)


@login_required
def follow_unfollow(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = get_object_or_404(Profile, user=target_user)

    if request.user == target_user:
        messages.error(request, "You cannot follow yourself.")
    else:
        if request.user in target_profile.followers.all():
            target_profile.followers.remove(request.user)
            messages.success(request, f"You unfollowed {target_user.username}")
        else:
            target_profile.followers.add(request.user)
            messages.success(request, f"You followed {target_user.username}")

    return redirect("view_profile", username=username)

# ---------------------------
# API Views
# ---------------------------
@api_view(['GET'])
def profile_list(request):
    paginator = PageNumberPagination()
    paginator.page_size = 10
    profiles = Profile.objects.all()
    result_page = paginator.paginate_queryset(profiles, request)
    serializer = ProfileDetailSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)

# ---------------------------
# Home View
# ---------------------------
def home(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return redirect('login')



@login_required
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    current_profile = request.user.profile

    # Add current user to target's followers
    target_profile.followers.add(request.user)

    # Add target user to current's following
    current_profile.following.add(target_user)

    return redirect("view_profile", username=username)


@login_required
def unfollow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile
    current_profile = request.user.profile

    # Remove current user from target's followers
    target_profile.followers.remove(request.user)

    # Remove target user from current's following
    current_profile.following.remove(target_user)

    return redirect("view_profile", username=username)

@login_required
def follow(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile

    if target_profile != request.user.profile:  # prevent self-follow
        request.user.profile.following.add(target_profile)

    return redirect("view_profile", username=username)

@login_required
def unfollow(request, username):
    target_user = get_object_or_404(User, username=username)
    target_profile = target_user.profile

    if target_profile != request.user.profile:
        request.user.profile.following.remove(target_profile)

    return redirect("view_profile", username=username)


