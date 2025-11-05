from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<str:username>/', views.start_conversation, name='start_conversation'),
    path('<int:conversation_id>/', views.chat_room, name='chat_room'),
    path('<int:conversation_id>/messages/', views.get_conversation_messages, name='get_messages'),
] 