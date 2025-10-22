"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tasks.views import MyLoginView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ✅ All your app URLs
    path("", include(("tasks.urls", "tasks"), namespace="tasks")),

    # ✅ Django admin (separate)
    path("admin/", admin.site.urls),

    # ✅ Django's default login redirect
    path("accounts/login/", MyLoginView.as_view(), name="login_redirect"),

     # ✅ Add this line:
    path('i18n/', include('django.conf.urls.i18n')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)