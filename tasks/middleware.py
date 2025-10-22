from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import UserActivity
from django.contrib.auth.models import AnonymousUser
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class UserActivityMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and not isinstance(request.user, AnonymousUser):
            #log only on login page or once per session
            if not request.session.get('has_logged_activity', False):
                ip = self.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                UserActivity.objects.create(
                    user=request.user,
                    login_time=timezone.now(),
                    ip_address=ip,
                    user_agent=user_agent
                ) 
                request.session['has_logged_activity'] = True
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        return ip
    
class BlockedUserLogoutMiddleware(MiddlewareMixin):
    """
    If user.status == 'blocked' ensure they are logged out and redirected to login with a message.
    Add this middleware near the top (after AuthenticationMiddleware).
    """
    def process_request(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            try:
                if getattr(user, "status", None) == user.Status.BLOCKED:
                    logout(request)
                    # simplest redirect to login (could include message via next + query param)
                    return redirect(reverse('tasks:login') + "?blocked=1")
            except Exception:
                # be defensive: don't break requests if something odd
                pass
        return None