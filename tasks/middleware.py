from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import UserActivity
from django.contrib.auth.models import AnonymousUser


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