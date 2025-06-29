from django.urls import path
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('profile/<str:username>/', views.profile, name='profile_by_username'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('create_post/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('like_post/<int:post_id>/', views.like_post, name='like_post'),
    path('comment_post/<int:post_id>/', views.comment_post, name='comment_post'),
    path('users/', views.user_list, name='user_list'),
    path('follow/<int:user_id>/', views.follow_user, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow'),
    path('logout/', views.custom_logout, name='logout'),
    path('messages/', views.user_messages, name='messages'),
    path('chats/', views.chats, name='chats'),
    path('chat/<str:username>/', views.chat_room, name='chat_room'),
    path('chat/send_message/', views.chat_send_message, name='chat_send_message'),
    path('search/', views.search, name='search'),
]

