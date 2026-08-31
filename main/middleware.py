from django.shortcuts import redirect
from django.contrib import messages
from django.urls import resolve, Resolver404


PAYMENT_PREFIXES     = ('/finance/payments/', '/finance/reports/')
ENROLLMENT_PREFIXES  = ('/finance/enrollments/',)
ACADEMIC_PREFIXES    = ('/portal/students/', '/portal/classes/', '/portal/subjects/',
                        '/portal/grades/', '/portal/reports/')
TEACHER_MGT_PREFIXES = ('/portal/teachers/', '/portal/periods/')
SETTINGS_PREFIXES    = ('/settings/',)
USER_PREFIXES        = ('/users/',)


def _get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class RoleAccessMiddleware:
    """Block access to sections the user's role doesn't permit."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            path = request.path
            try:
                profile = request.user.profile
            except Exception:
                from main.models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user)

            denied = False

            if any(path.startswith(p) for p in PAYMENT_PREFIXES):
                denied = not profile.can_manage_payments
            elif any(path.startswith(p) for p in ENROLLMENT_PREFIXES):
                denied = not profile.can_manage_enrollments
            elif any(path.startswith(p) for p in ACADEMIC_PREFIXES):
                denied = not profile.can_manage_academic
            elif any(path.startswith(p) for p in TEACHER_MGT_PREFIXES):
                denied = not profile.can_manage_teachers
            elif any(path.startswith(p) for p in SETTINGS_PREFIXES):
                denied = not profile.can_manage_settings
            elif any(path.startswith(p) for p in USER_PREFIXES):
                denied = not profile.can_manage_users

            if denied:
                messages.error(request, "Accès refusé : vous n'avez pas les droits nécessaires.")
                return redirect('dashboard')

        return self.get_response(request)


class SessionActivityMiddleware:
    """Store IP + user-agent in session on each request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if 'login_ip' not in request.session:
                request.session['login_ip'] = _get_client_ip(request)
            if 'login_ua' not in request.session:
                request.session['login_ua'] = request.META.get('HTTP_USER_AGENT', '')[:200]

        return self.get_response(request)
