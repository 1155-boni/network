from .models import Message 
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post
from .models import Profile

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('caption', 'image')
        
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name"]

class UserUpdateForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    last_name  = forms.CharField(required=False)
    email      = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control"}),
            "username":   forms.TextInput(attrs={"class": "form-control"}),
            "email":      forms.EmailInput(attrs={"class": "form-control"}),
        }

class ProfileForm(forms.ModelForm):
    bio        = forms.CharField(required=False, widget=forms.Textarea(attrs={"class": "form-control", "rows": 3}))
    location   = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "form-control"}))
    profile_pic = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ["bio", "location", "profile_pic"]
class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 2, "placeholder": "Type a message..."}),
        }
