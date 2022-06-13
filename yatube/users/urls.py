from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('logout/', LogoutView.as_view(
        template_name='users/logged_out.html'), name='logout'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('login/', LoginView.as_view(
        template_name='users/login.html'), name='login'),
    path('passchange/', PasswordChangeView.as_view(
        template_name='users/password_change_form.html'), name='passchange'),
    path('passchangedone/', PasswordChangeView.as_view(
        template_name='users/password_change_done.html'),
        name='passchangedone'),
    path('passreset/', PasswordResetView.as_view(
        template_name='users/password_reset_form.html'), name='passreset'),
    path('passresetconf/', PasswordResetView.as_view(
        template_name='users/password_reset_confirm.html'),
        name='passresetconf'),
]
