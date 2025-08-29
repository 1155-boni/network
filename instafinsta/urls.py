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
    path("profile/", views.profile, name="my_profile"),  
    path("profile/<str:username>/", views.profile, name="profile"),
    path("explore/", views.explore, name="explore"),
    path("post/<int:post_id>/", views.post_detail, name="post_detail"),
    path("profile/<str:username>/", views.view_profile, name="view_profile"),
    path("profile/<str:username>/follow/", views.follow_toggle, name="follow_toggle"),
    path("follow/<str:username>/", views.follow_unfollow, name="follow_unfollow"),
    path('api/profiles/', views.profile_list, name="profile-list"),
]