from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser, Profile

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
    # Get or create profile for current user
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            # Redirect to user's profile page
            return redirect('users:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'users/edit_profile.html', {'form': form})
 