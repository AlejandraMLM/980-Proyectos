from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import LockoutAuthenticationForm


class LockoutLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LockoutAuthenticationForm

    def get_success_url(self):
        """
        Redirecciona según el rol del usuario:
        - Veterinario  -> veterinario:panel
        - Superusuario -> administrador:inicio (tu panel admin actual)
        - Administrador (si usas tipo_usuario) -> administrador:inicio
        - Cliente/otros -> mascotas:listar
        """
        user = self.request.user

        # Primero si es superusuario (mantengo tu panel admin existente)
        if getattr(user, "is_superuser", False):
            try:
                return self.request.build_absolute_uri(self.request.resolver_match.reverse('administrador:inicio'))
            except Exception:
                return "/admin/"

        # Si usas el campo tipo_usuario en tu modelo Usuario
        tipo = getattr(user, "tipo_usuario", "") or ""
        if tipo == "veterinario":
            return self.request.build_absolute_uri(self.request.resolver_match.reverse('veterinario:panel')) \
                if self.request.resolver_match else "/veterinario/"
        if tipo == "administrador":
            return self.request.build_absolute_uri(self.request.resolver_match.reverse('administrador:inicio')) \
                if self.request.resolver_match else "/admin/"

        # Cliente u otros
        try:
            return self.request.build_absolute_uri(self.request.resolver_match.reverse('mascotas:listar'))
        except Exception:
            return "/"

@login_required
def redirigir_por_rol(request):
    """
    Útil si en algún momento quieres redirigir por rol desde otra parte.
    """
    u = request.user
    if getattr(u, "is_superuser", False):
        return redirect('administrador:inicio') if _has_url(request, 'administrador:inicio') else redirect('/admin/')
    tipo = getattr(u, "tipo_usuario", "") or ""
    if tipo == "veterinario":
        return redirect('veterinario:panel') if _has_url(request, 'veterinario:panel') else redirect('/veterinario/')
    if tipo == "administrador":
        return redirect('administrador:inicio') if _has_url(request, 'administrador:inicio') else redirect('/admin/')
    return redirect('mascotas:listar') if _has_url(request, 'mascotas:listar') else redirect('/')


def _has_url(request, name: str) -> bool:
    """
    Verifica si existe una URL reversable por nombre (evita errores si cambian namespaces).
    """
    try:
        request.resolver_match.reverse(name)  # type: ignore[attr-defined]
        return True
    except Exception:
        try:
            from django.urls import reverse
            reverse(name)
            return True
        except Exception:
            return False
