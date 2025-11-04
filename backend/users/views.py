from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser, Profile
from django.db.models import Q 
from posts.models import Post
from followers.models import Follow

def search_view(request):
    query = request.GET.get('q', '')
    results = {
        'users': [],
        'posts': []
    }
    
    if query:
        # Search users by username or bio
        results['users'] = CustomUser.objects.filter(
            Q(username__icontains=query) | 
            Q(profile__bio__icontains=query)
        ).select_related('profile')
    
    return render(request, 'users/search_results.html', {
        'query': query,
        'results': results
    })


def landing(request):
    return render(request, 'landing.html') 


def home(request):
    return render(request, 'home.html')



# ---------------------------
# REGISTER VIEW
# ---------------------------
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Save user
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()

            # Create profile manually since signals are deleted
            Profile.objects.get_or_create(user=user)

            # Log in user
            auth_login(request, user)
            messages.success(request, "Welcome! Your account has been created successfully.")

            # Redirect to profile edit page
            return redirect('users:edit_profile')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


# ---------------------------
# PROFILE VIEW
# ---------------------------
@login_required
def profile_view(request, username=None):
    if username:
        user_obj = get_object_or_404(CustomUser, username=username)
    else:
        user_obj = request.user

    # Ensure profile exists
    Profile.objects.get_or_create(user=user_obj)
    
    # Calculate real counts
    posts_count = Post.objects.filter(author=user_obj).count()
    followers_count = user_obj.follower_relationships.count()
    following_count = user_obj.following_relationships.count()
    
    # Check if current user follows this profile user
    is_following = False
    if request.user.is_authenticated and request.user != user_obj:
        is_following = Follow.objects.filter(
            follower=request.user, 
            following=user_obj
        ).exists()

    return render(request, 'users/profile.html', {
        'user_obj': user_obj,
        'posts_count': posts_count,
        'followers_count': followers_count,
        'following_count': following_count,
        'is_following': is_following,
    })


# ---------------------------
# EDIT PROFILE VIEW
# ---------------------------
@login_required
def edit_profile_view(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            profile = form.save(commit=False)

            # Handle username update
            new_username = form.cleaned_data.get("username")
            if new_username and new_username != request.user.username:
                request.user.username = new_username
                request.user.save()

            profile.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('users:profile', username=request.user.username)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile, user=request.user)

    return render(request, 'users/edit_profile.html', {'form': form})