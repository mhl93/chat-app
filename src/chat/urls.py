from django.urls import path
from .views import (
    MGroupListCreateView,
    MGroupDetailView,
    MessageListCreateView,
    MessageDetailView,
    MessageGroupWithMessageListView,
)

urlpatterns = [
    path("groups/", MGroupListCreateView.as_view(), name="mgroup-list-create"),
    path("groups/<int:pk>/", MGroupDetailView.as_view(), name="mgroup-detail"),
    path("messages/", MessageListCreateView.as_view(), name="message-list-create"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message-detail"),
    path(
        "mgroup-messages/",
        MessageGroupWithMessageListView.as_view(),
        name="mgroup-messages-list",
    ),
]
