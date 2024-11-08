from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='signup'),
    path('register/verify/<str:otp_secret>/', views.VerifyView.as_view(), name='verify'),

]