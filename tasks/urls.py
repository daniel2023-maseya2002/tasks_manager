from django.urls import path
from .views import signup_view, MyLoginView, MyLogoutView, dashboard_view
from django.contrib.auth import views as auth_views
from . import views

app_name = "tasks"

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", MyLogoutView.as_view(), name="logout"),
    path("", dashboard_view, name="dashboard"),  # root of tasks app -> dashboard
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/update/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),
]