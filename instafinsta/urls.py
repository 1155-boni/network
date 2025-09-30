from django.urls import path
from instafinsta import views
from network import settings
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('post/', create_post, name='create_post'),
    path('messages/<int:user_id>/', message_thread, name='messages'),
    path('feed/', feed, name='feed'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/remove-pic/', remove_profile_pic, name='remove_profile_pic'),
    path('messages/', inbox, name='inbox'),
    path('messages/with/<int:user_id>/', messages_with, name='messages_with'),
    path('messages/list/', messages_list, name='messages_list'),
    path("explore/", explore, name="explore"),
    path("post/<int:post_id>/", post_detail, name="post_detail"),
    path("toggle-follow/<str:username>/", views.toggle_follow, name="follow_toggle"),
    path("toggle-like/<int:post_id>/", views.toggle_like, name="toggle_like"),
    path('api/profiles/', profile_list, name="profile-list"),
    path("post/<int:post_id>/delete/", delete_post, name="delete_post"),
    path("comment/<int:post_id>/", add_comment, name="add_comment"),
    path("send/<int:user_id>/", send_message, name="send_message"),
    # profile URLs
    path("profile/", profile, name="my_profile"),
    path("profile/<str:username>/", profile, name="view_profile"),
    path("unread-messages-count/", unread_count, name="unread_count"),
    path("messages/<int:user_id>/", views.message_thread, name="message_thread"),
    path('create_test_user/', views.create_test_user, name='create_test_user'),
]
