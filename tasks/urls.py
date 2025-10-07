from django.urls import path
from django.contrib import admin
from . import views
from .views import signup_view, MyLoginView, my_logout_view, dashboard_view

app_name = "tasks"

urlpatterns = [
    path("", MyLoginView.as_view(), name="login_redirect"),  # root → login
    path("signup/", signup_view, name="signup"),
    path("login/", MyLoginView.as_view(), name="login"),
    path("logout/", my_logout_view, name="logout"),
    path("dashboard/", dashboard_view, name="dashboard"),

    # ✅ Tasks
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/create/", views.task_create, name="task_create"),
    path("tasks/<int:pk>/update/", views.task_update, name="task_update"),
    path("tasks/<int:pk>/delete/", views.task_delete, name="task_delete"),

    # ✅ User management (custom)
    path("users/manage/", views.manage_users, name="manage_users"),
    path("users/create/", views.create_user, name="create_user"),
    path("users/<int:user_id>/edit/", views.edit_user, name="edit_user"),
    path("users/<int:user_id>/delete/", views.delete_user, name="delete_user"),

    path('user-list/', views.user_list, name='user_list'),
    path("tasks/<int:task_id>/status/", views.update_task_status, name="update_task_status"),


    # ✅ Django admin
    path("admin/", admin.site.urls),
]
