from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Follow

User = get_user_model()

@login_required
def follow_toggle(request, username):  # ✅ This function must exist
    user_to_follow = get_object_or_404(User, username=username)
    
    if request.user == user_to_follow:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'You cannot follow yourself'}, status=400)
        return redirect('users:profile', username=username)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        follow.delete()
        is_following = False
    else:
        is_following = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_following': is_following,
            'followers_count': user_to_follow.follower_relationships.count(),
            'following_count': request.user.following_relationships.count()
        })
    
    return redirect('users:profile', username=username)

@login_required
def followers_list(request, username):  # ✅ This function must exist
    user = get_object_or_404(User, username=username)
    followers = User.objects.filter(following_relationships__following=user)
    
    return render(request, 'followers/followers_list.html', {
        'profile_user': user,
        'users': followers,
        'page_type': 'followers',
        'followers_count': user.follower_relationships.count(),
        'following_count': user.following_relationships.count(),
    })

@login_required
def following_list(request, username):  # ✅ This function must exist
    user = get_object_or_404(User, username=username)
    following = User.objects.filter(follower_relationships__follower=user)
    
    return render(request, 'followers/following_list.html', {
        'profile_user': user,
        'users': following,
        'page_type': 'following',
        'followers_count': user.follower_relationships.count(),
        'following_count': user.following_relationships.count(),
    })