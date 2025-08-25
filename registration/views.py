
from django.shortcuts import render,redirect
from django.http import HttpResponse
from .forms import *
from .models import *
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def sign_up(request):
    context = {

        'form' : None,
        'errors': None,
        'user':request.user
    }
    if request.method == "POST":
        form = SignUpForm(request.POST)
        form.user = request.user.id
        if form.is_valid():
            form.save()
            return sign_in(request)
        else:
            context['errors'] = form.errors
    if  context['user'].username:
        return redirect('home')

    form = SignUpForm()
    context['form'] = form
    return render(request,'register.html', context)

def sign_in(request):
    if  request.user.username:
        return redirect('home')
    if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password1']
            user = authenticate(request,username=username,password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  
            else:
                return render(request, 'login.html', {'error': 'Invalid credentials'})
        
    return render(request, 'login.html')
def sign_out(request):
    logout(request)
    return redirect('home')
