
from django.urls import path
from .views import (
    RegisterUserView, LoginView, UserProfileView,
    AdminUserDetailView, UserListView
)

app_name = "users"

urlpatterns = [
    # Public-facing endpoints
    path("auth/register/", RegisterUserView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),

    # Authenticated user profile
    path("me/", UserProfileView.as_view(), name="profile"),

    # Admin-only endpoints
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="user-detail"),
    path("admin/users/", UserListView.as_view(), name="user-list"),
]
