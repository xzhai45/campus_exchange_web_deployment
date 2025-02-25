from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("No user is associated with this email address.")
        return email

class CustomSetPasswordForm(SetPasswordForm):
    pass

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'phone_number', 'profile_picture']

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not email.endswith(".edu"):
            raise forms.ValidationError("Only .edu emails are allowed.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_verified = False  # Set user as unverified initially
        if commit:
            user.save()
            self.send_verification_email(user)  # Send verification email
        return user

    def send_verification_email(self, user):
        verification_url = f"{settings.SITE_URL}/accounts/verify/{user.verification_token}/"
        subject = "Verify Your Email Address"
        message = f"Hello, please click the following link to verify your email address: {verification_url}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])