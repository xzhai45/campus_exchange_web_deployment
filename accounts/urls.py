from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView


urlpatterns = [
    path('signup', views.signup, name='accounts.signup'),
    path('login', views.login, name='accounts.login'),
    path('logout/', views.logout, name='accounts.logout'),
    path('verify/<uuid:token>/', views.verify_email, name='accounts.verify_email'),
    path('profile/', views.profile_view, name='accounts.profile'),
    path('password-reset/', CustomPasswordResetView.as_view(), name='accounts.password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='accounts.password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='accounts.password_reset_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)