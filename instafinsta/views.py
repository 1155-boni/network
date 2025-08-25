from django.contrib import messages
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import *
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully')
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, 'Logged in successfully')
                return redirect('profile')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')




@login_required
def profile(request):
    if request.method == 'POST' and 'profile_pic' in request.FILES:
        profile = request.user.profile
        profile.profile_pic = request.FILES['profile_pic']
        profile.save()
        messages.success(request, 'Profile picture updated!')
        return redirect('profile')
    return render(request, 'profile.html', {'user': request.user})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            # Set content if not in form
            post.content = request.POST.get('content', '')
            post.save()
            messages.success(request, 'Post created successfully')
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'post.html', {'form': form})
