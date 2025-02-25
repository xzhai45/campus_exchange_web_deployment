from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
import re
from .forms import CustomUserCreationForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm


from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from .forms import CustomPasswordResetForm, CustomSetPasswordForm


User = get_user_model()

class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    subject_template_name = "accounts/password_reset_subject.txt"
    success_url = reverse_lazy('accounts.password_reset_done')
    form_class = CustomPasswordResetForm

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy('accounts.password_reset_complete')
    form_class = CustomSetPasswordForm


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('accounts.profile')
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def logout(request):
    auth_logout(request)
    return redirect('home.index')

def signup(request):
    template_data = {'title': 'Sign Up'}

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "We've sent a verification link to your email. Please check your inbox or junk folder and verify your email before logging in.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    template_data['form'] = form
    return render(request, 'accounts/signup.html', {'template_data': template_data})

def verify_email(request, token):
    try:
        user = CustomUser.objects.get(verification_token=token)
        if not user.is_verified:
            user.is_verified = True
            user.save()
            messages.success(request, "Email successfully verified! You can now log in.")
        else:
            messages.info(request, "Your email is already verified.")
    except CustomUser.DoesNotExist:
        messages.error(request, "Invalid verification link.")
    
    return redirect('accounts.signup')

def login(request):
    template_data = {'title': 'Login'}

    if request.method == 'GET':
        return render(request, 'accounts/login.html', {'template_data': template_data})

    elif request.method == 'POST':
        email = request.POST.get('username')  # Using 'username' as input field for email
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is None:
            template_data['error'] = 'The email or password is incorrect.'
            return render(request, 'accounts/login.html', {'template_data': template_data})

        elif not user.is_verified and not user.is_superuser:
            template_data['error'] = 'Please verify your email before logging in.'
            return render(request, 'accounts/login.html', {'template_data': template_data})

        else:
            auth_login(request, user)
            return redirect('home.index')