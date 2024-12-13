from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from django.db.models import Count
from datetime import datetime


class NotificationAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request):
        notifications = self.get_queryset()

        paginator = self.paginate_queryset(notifications)
        if paginator is not None:
            serialized_notifications = self.get_serializer(paginator, many=True)
            return self.get_paginated_response(serialized_notifications.data)
        else:
            serialized_notifications = self.get_serializer(notifications, many=True)
            data = {
                'count': len(serialized_notifications.data),
                'next': None,
                'previous': None,
                'results': serialized_notifications.data,
            }
            return Response(data)

    def get_serializer_class(self):
        from .serializers import NotificationSerializer
        return NotificationSerializer
