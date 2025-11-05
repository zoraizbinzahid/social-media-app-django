from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Conversation, Message

# Create your views here.


User = get_user_model()

@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is participant in conversation
    if request.user not in conversation.participants.all():
        return redirect('chat:inbox')
    
    messages = conversation.messages.all().select_related('sender')
    other_user = conversation.participants.exclude(id=request.user.id).first()
    
    return render(request, 'chat/chat_room.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
    })

@login_required
def inbox(request):
    # Get all conversations for current user
    conversations = request.user.conversations.all().prefetch_related('participants', 'messages')
    
    return render(request, 'chat/inbox.html', {
        'conversations': conversations,
    })

@login_required
def start_conversation(request, username):
    other_user = get_object_or_404(User, username=username)
    
    # Find existing conversation or create new one
    conversation = Conversation.objects.filter(participants=request.user).filter(participants=other_user).first()
    
    if not conversation:
        conversation = Conversation.objects.create()
        conversation.participants.add(request.user, other_user)
    
    return redirect('chat:chat_room', conversation_id=conversation.id)

@login_required
def get_conversation_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Not authorized'}, status=403)
    
    messages = conversation.messages.all().select_related('sender')
    messages_data = []
    
    for message in messages:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender': message.sender.username,
            'sender_id': message.sender.id,
            'timestamp': message.timestamp.isoformat(),
            'is_read': message.is_read,
        })
    
    return JsonResponse({'messages': messages_data})