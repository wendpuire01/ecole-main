def user_role(request):
    """Inject role flags into every template context."""
    if not request.user.is_authenticated:
        return {
            'user_role': None,
            'user_profile': None,
            'can_manage_finance': False,
            'can_manage_academic': False,
            'can_manage_users': False,
            'can_manage_settings': False,
            'is_admin': False,
            'is_director': False,
        }

    try:
        profile = request.user.profile
    except Exception:
        from main.models import UserProfile
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return {
        'user_role': profile.role,
        'user_profile': profile,
        'can_manage_finance': profile.can_manage_finance,
        'can_manage_academic': profile.can_manage_academic,
        'can_manage_users': profile.can_manage_users,
        'can_manage_settings': profile.can_manage_settings,
        'is_admin': profile.is_admin,
        'is_director': profile.is_director,
    }
