from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser, Profile
from django.db.models import Q 



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
        user = get_object_or_404(CustomUser, username=username)
    else:
        user = request.user

    # Ensure profile exists
    Profile.objects.get_or_create(user=user)

    return render(request, 'users/profile.html', {'user_obj': user})


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



from django.db.models import Q

def search_view(request):
    query = request.GET.get('q', '')
    results = {
        'users': [],
        'posts': []
    }
    
    if query:
        # Search users
        results['users'] = CustomUser.objects.filter(
            Q(username__icontains=query) | 
            Q(profile__bio__icontains=query)
        ).select_related('profile')
        
        # Search posts (when you create posts app)
        # results['posts'] = Post.objects.filter(
        #     Q(content__icontains=query) |
        #     Q(author__username__icontains=query)
        # )
    
    return render(request, 'users/search_results.html', {
        'query': query,
        'results': results
    })