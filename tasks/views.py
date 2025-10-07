from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout, get_user_model
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm, TaskForm
from .models import Task, CustomUser, Notification
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.http import HttpResponseForbidden
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User


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

    # Tasks: all for superuser, filtered for normal users
    if user.is_superuser:
        tasks = Task.objects.all().order_by('-created_at')
    else:
        tasks = Task.objects.filter(Q(owner=user) | Q(assigned_to=user)).distinct().order_by('-created_at')

    # Task counts for summary cards
    pending_count = tasks.filter(status="Pending").count()
    in_progress_count = tasks.filter(status="In Progress").count()
    completed_count = tasks.filter(status="Completed").count()

    # Latest 5 notifications for this user
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]

    context = {
        "tasks": tasks,
        "pending_count": pending_count,
        "in_progress_count": in_progress_count,
        "completed_count": completed_count,
        "notifications": notifications,
    }
    return render(request, "tasks/dashboard.html", context)


@login_required
def task_list(request):
    # Start with all tasks
    tasks = Task.objects.all()

    # Get filter parameters from GET request
    search = request.GET.get("search", "").strip()
    status = request.GET.get("status", "").strip()
    assigned_to = request.GET.get("assigned_to", "").strip()

    # Admin sees all tasks, normal users see only their own or assigned ones
    if not (request.user.is_superuser or getattr(request.user, "role", "") == "admin"):
        tasks = tasks.filter(Q(owner=request.user) | Q(assigned_to=request.user))

    # ✅ Filter by status
    if status:
        # Case-insensitive match for the status field
        tasks = tasks.filter(status__iexact=status)

    # ✅ Filter by assigned_to username (case-insensitive)
    if assigned_to:
        tasks = tasks.filter(assigned_to__username__icontains=assigned_to)

    # ✅ Filter by title or description
    if search:
        tasks = tasks.filter(Q(title__icontains=search) | Q(description__icontains=search))

    # Order newest first
    tasks = tasks.order_by("-created_at")

    context = {
        "tasks": tasks,
        "search_query": search,
        "status_filter": status,
        "assigned_to_filter": assigned_to,
    }

    return render(request, "tasks/task_list.html", context)


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

@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Check Permission
    if not (request.user.is_superuser or request.user == task.owner or request.user == task.assigned_to):
        messages.error(request, "You do not have permission to change tasks")
        return redirect('tasks:task_list')
    

    if request.method == "POST":
        new_status = request.POST.get("status")
        valid_statues =  ["Pending", "In Progress", "Completed"]
        if new_status in valid_statues:
            task.status = new_status
            # Sync is_completed with status
            task.is_completed = (new_status == "Completed")
            task.save()
            messages.success(request, f"Task '{task.title}' status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status selected")
        return redirect('tasks:task_list')
    
    return render(request, "tasks/update_task_status.html", {"task": task})



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


# Utility to check if user is admin
def is_admin(user):
    return user.is_superuser or user.is_staff



# Admin: View All users
@login_required
@user_passes_test(is_admin)
def manage_users(request):
    # Get search and role filter parameters
    search_query = request.GET.get("search", "")
    role_filter = request.GET.get("role", "")

    # Get all users
    users = CustomUser.objects.all()

    # Filter by username (case-insensitive)
    if search_query:
        users = users.filter(username__icontains=search_query)

    # Filter by role using is_staff
    if role_filter:
        if role_filter.lower() == "admin":
            users = users.filter(is_staff=True)
        elif role_filter.lower() == "user":
            users = users.filter(is_staff=False)

    context = {
        "users": users,
        "search_query": search_query,
        "role_filter": role_filter,
    }

    return render(request, "tasks/manage_users.html", context)


# Admin create a new user
@login_required
@user_passes_test(is_admin)
def create_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = "user" # default
            user.save()
            messages.success(request, "User created successfully!")
            return redirect("tasks:manage_users")
        
    else:
        form = CustomUserCreationForm()
    return render(request, "tasks/create_user.html", {"form": form})



# Admin: Edit user
@login_required
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request,"User updated successfully!")
            return redirect("tasks:manage_users")
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, "tasks/edit_user.html", {"form": form, "user": user})


# Admin: Delete user
@login_required
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(request, user_id)
    user.delete()
    messages.success(request, "User Deleted Successfully!")
    return redirect("tasks:manage_users")


@login_required
@user_passes_test(lambda u: u.is_superuser)
def redirect_admin_users(request):
    return redirect("tasks:manage_users")


@login_required
def delete_user(request, user_id):

    #Allow only rel admins or superuser
    if not (request.user.is_superuser or request.user.role == "admin"):
        raise PermissionDenied
    
    user_obj = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        user_obj.delete()
        messages.success(request, "User deleted succefully!")
        return redirect("tasks:manage_users")
    
    # for Get show the confirmation page
    return render(request, "tasks/delete_user.html", {"user_obj": user_obj})


# Only admins can access
@user_passes_test(lambda u: u.is_superuser)
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, "user_list.html", {'users': users})




