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
    path('messages/<int:user_id>/', message_thread, name='messages'),
    path('feed/', feed, name='feed'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/remove-pic/', remove_profile_pic, name='remove_profile_pic'),
    path('messages/', inbox, name='inbox'),
    path("messages/<int:user_id>/", views.messages_with, name="messages_with"),

]