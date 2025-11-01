from django.urls import path 
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.feed_views, name='feed'),
    path('create/', views.create_post, name='create_post'),
    path('<int:pk./', views.post_detail, name='post_detail'),
    path('<int:pk>/like/', views.like_post, name='like_post'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('<int:pk>/delete/', views.delete_post, name='delete_post'),
]