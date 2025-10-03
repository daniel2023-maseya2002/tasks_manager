from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.views import LoginView, LogoutView
from .forms import CustomUserCreationForm
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
    redirect_authenticated_user = True  # redirect logged-in users away from login page


class MyLogoutView(LogoutView):
    next_page = reverse_lazy("tasks:login")


@login_required
def dashboard_view(request):
    # simple dashboard — we'll expand later
    return render(request, "tasks/dashboard.html", {})
