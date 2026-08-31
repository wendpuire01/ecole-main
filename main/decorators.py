from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Restrict access to users whose profile.role is in `roles`."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            try:
                if request.user.profile.role in roles:
                    return view_func(request, *args, **kwargs)
            except Exception:
                pass
            messages.error(request, "Vous n'avez pas la permission d'accéder à cette page.")
            return redirect('dashboard')
        return _wrapped
    return decorator


def admin_required(view_func):
    return role_required('admin', 'founder')(view_func)


def finance_required(view_func):
    return role_required('admin', 'founder', 'director', 'cashier')(view_func)


def academic_required(view_func):
    return role_required('admin', 'founder', 'director', 'educator')(view_func)


def management_required(view_func):
    return role_required('admin', 'founder', 'director')(view_func)
