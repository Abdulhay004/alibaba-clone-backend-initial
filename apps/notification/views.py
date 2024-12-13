from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from django.db.models import Count
from datetime import datetime
from .serializers import NotificationSerializer


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

class NotificationDetailAndUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_object(self):
        try:
            notification = Notification.objects.get(id=self.kwargs['id'], user=self.request.user)
            return notification
        except Notification.DoesNotExist:
            return Response({'detail': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)


    def retrieve(self, request, *args, **kwargs):
        notification = self.get_object()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)


    def update(self, request, *args, **kwargs):
        groups = request.user.groups.first()
        if groups == None:
            return Response(status=403)
        notification = self.get_object()
        serializer = self.get_serializer(notification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
