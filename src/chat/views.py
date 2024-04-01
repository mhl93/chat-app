from rest_framework import generics, permissions
from .models import MGroup, Message
from .serializers import MGroupSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


class MGroupListCreateView(generics.ListCreateAPIView):
    serializer_class = MGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter MGroups where the request user is a member
        return MGroup.objects.filter(member=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the creator to the request user
        serializer.save(creator=self.request.user)


class MGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MGroup.objects.all()
    serializer_class = MGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensures users can only access their own MGroups
        return self.queryset.filter(creator=self.request.user)


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter Messages sent by the request user
        return Message.objects.filter(sender=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the sender to the request user
        serializer.save(sender=self.request.user)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Ensures users can only access their own Messages
        return self.queryset.filter(sender=self.request.user)


class MessageGroupWithMessageListView(generics.ListAPIView):
    serializer_class = MGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            MGroup.objects.filter(member=self.request.user)
            .prefetch_related("messages")
            .order_by("-id")
        )
