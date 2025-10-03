from django.urls import path
from .views import signup_view, MyLoginView, MyLogoutView, dashboard_view
from django.contrib.auth import views as auth_views

app_name = "tasks"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("", dashboard_view, name="dashboard"),  # root of tasks app -> dashboard
]