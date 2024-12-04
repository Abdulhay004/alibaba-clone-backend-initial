from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='signup'),
    path('register/verify/<str:otp_secret>/', views.VerifyView.as_view(), name='verify'),
    path('login/', views.LoginView.as_view(), name='login'),
    # path('me/', views.UsersMeView.as_view(), name='users-me'),
    path('change/password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password/forgot/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('password/forgot/verify/<str:otp_secret>/', views.ForgotVerifyView.as_view(), name='forgot-verify'),
    path('password/reset/', views.ResetPasswordView.as_view(), name='reset-password'),
    path('logout/', views.LogoutView.as_view(), name='logout-view')
]