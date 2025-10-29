from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, ProfileForm
from .models import CustomUser

# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get('email')
            user.save()
            # auto-created profile via signals
            auth_login(request, "Welcome! Your account has been created successfully.")
            #redirect after signup
            #prefer sendding to profile edit so user can complete profile
            return redirect('users:edit_profile')
        
        else:
            form = CustomUserCreationForm()
        return render(redirect, 'users/register.html', {'form': form})
    

@login_required
def profile_view(request, username=None):
    # if username given, view that user; otherwise current user
    if username:
        user = get_object_or_404(CustomUser, username=username)
    else:
        user = request.user
    return render(request, 'users/profile.html', {'user_obj': user})

@login_required
def edit_profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            #After editing profile, redirect to personal profile page
            return redirect('users:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'users/edit_profile.html', {'form': form})
