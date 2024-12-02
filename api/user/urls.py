from django.urls import path
from .views import RegisterView, ActivateAccountView, LoginView, LogoutView, PasswordResetRequestView, PasswordResetConfirmView

urlpatterns = [
    path('user/register', RegisterView.as_view(), name='register'),
    path('user/activate/<int:user_id>', ActivateAccountView.as_view(), name='activate'),
    path('user/login', LoginView.as_view(), name='login'),
    path('user/logout', LogoutView.as_view(), name='logout'),
    path('user/password-reset', PasswordResetRequestView.as_view(), name='password-reset-request'),
    path('user/reset-password/<int:user_id>/<str:token>', PasswordResetConfirmView.as_view(), name='password-reset-confirm')
]