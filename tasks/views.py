from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, TaskForm
from .models import Task
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponseForbidden
from django.db.models import Q

User = get_user_model()

# Create your views here.
def signup_view(request):
    """Register new users."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully. Please log in.")
            return redirect("tasks:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "tasks/signup.html", {"form": form})


class MyLoginView(LoginView):
    template_name = "tasks/login.html"
    #redirect_authenticated_user = False  # redirect logged-in users away from login page


def my_logout_view(request):
    """Logout user via GET and redirect to login page."""
    logout(request)
    return redirect(reverse_lazy("tasks:login"))

@login_required
def dashboard_view(request):
    user = request.user

    if user.is_superuser:
        tasks = Task.objects.all().order_by('-created_at')
        users = User.objects.all()
    else:
        # Regular users see tasks they own or are assigned to
        tasks = Task.objects.filter(Q(owner=user) | Q(assigned_to=user)).distinct().order_by('-created_at')
        users = None  # normal users can't see others

    context = {
        "tasks": tasks,
        "users": users,
    }
    return render(request, "tasks/dashboard.html", context)

# List all tasks
@login_required
def task_list(request):
    # Admin sees all tasks
    if request.user.is_superuser:
        tasks = Task.objects.all().order_by('-created_at')
    else:
        # Normal users see tasks they own or are assigned to
        tasks = Task.objects.filter(Q(owner=request.user) | Q(assigned_to=request.user)).distinct().order_by('-created_at')

    return render(request, "tasks/task_list.html", {"tasks": tasks})
# Create a task
def task_create(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.owner = request.user # logged user is the creator
            task.save()
            return redirect("tasks:task_list")
    
    else:
        form = TaskForm()
    return render(request, "tasks/task_form.html", {"form": form})

#update a task
@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # only owner or admin can edit
    if not (request.user.is_superuser or task.assigned_to == request.user):
        messages.error(request, "You don’t have permission to edit this task.")
        return redirect("dashboard")
    
    if request.method == "POST":
        form =TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("tasks:task_list")
    else:
        form = TaskForm(instance=task)
    return render(request, "tasks/task_form.html", {"form": form})

#delete a task
@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Only owner or admin can delete
    if not (request.user.is_superuser or task.assigned_to == request.user):
        messages.error(request, "You don’t have permission to delete this task.")
        return redirect("dashboard")
    if request.method == "POST":
        task.delete()
        return redirect("tasks:task_list")

    # FIX: should be "tasks/task_confirm_delete.html"
    return render(request, "tasks/task_confirm_delete.html", {"task": task})
