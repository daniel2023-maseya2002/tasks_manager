from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, TaskForm
from .models import Task
from django.contrib.auth.decorators import login_required

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


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("tasks:login")


@login_required
def dashboard_view(request):
    # simple dashboard — we'll expand later
    return render(request, "tasks/dashboard.html", {})

# List Tasks
@login_required
def task_list(request):
    if request.user.role == "admin":
        tasks = Task.objects.all() # admin sees everything
    else:
        tasks = Task.objects.filter(owner=request.user) | Task.objects.filter(assigned_to=request.user)
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
    if request.user != task.owner and request.user.role != "admin":
        return redirect("tasks:task_list")
    
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
    if request.user != task.owner and request.user.role != "admin":
        return redirect("tasks:task_list")

    if request.method == "POST":
        task.delete()
        return redirect("tasks:task_list")

    # FIX: should be "tasks/task_confirm_delete.html"
    return render(request, "tasks/task_confirm_delete.html", {"task": task})
