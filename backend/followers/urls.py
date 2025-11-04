from django.urls import path
from . import views

app_name = 'followers'

urlpatterns = [
    path('<str:username>/follow/', views.follow_toggle, name='follow_toggle'),
    path('<str:username>/followers/', views.followers_list, name='followers_list'),
    path('<str:username>/following/', views.following_list, name='following_list'),
]