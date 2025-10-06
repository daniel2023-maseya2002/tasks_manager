from django.urls import path
from .views import signup_view, MyLoginView, my_logout_view, dashboard_view
from django.contrib.auth import views as auth_views
from . import views

app_name = "tasks"

urlpatterns = [
    path("", MyLoginView.as_view(), name="login_redirect"),  # root → login
    path("signup/", signup_view, name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", my_logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/update/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
]
