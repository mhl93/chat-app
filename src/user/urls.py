from django.urls import path
from .views import UserProfileView

urlpatterns = [
    path(
        "preferences/",
        UserProfileView.as_view(),
        name="current_user_preferences",
    ),
]
