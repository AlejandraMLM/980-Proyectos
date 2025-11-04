from functools import wraps
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    """
    Uso:
    @role_required('veterinario')
    @role_required('admin', 'veterinario')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                return redirect_to_login(request.get_full_path())
            if user.tipo_usuario in roles or user.is_superuser:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied("No tienes permiso para acceder a esta página.")
        return _wrapped
    return decorator
