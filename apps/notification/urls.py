from django.urls import path
from .views import NotificationAPIView, NotificationDetailAndUpdateView

urlpatterns = [
    path('', NotificationAPIView.as_view(), name='notifications'),
    path('<uuid:id>/', NotificationDetailAndUpdateView.as_view(), name='notifications-detail'),
]