from django.urls import path
from instafinsta import views
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('post/', create_post, name='create_post'),
]
