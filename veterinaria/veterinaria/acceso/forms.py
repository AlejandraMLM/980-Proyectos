from datetime import timedelta
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.cache import cache
from django.utils import timezone


def _client_ip(request):
    """Obtiene la IP real del cliente."""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "0.0.0.0")


class LockoutAuthenticationForm(AuthenticationForm):
    """
    Inicio de sesión con:
      - Límite por (usuario + IP): 3 intentos → bloqueo 1 hora
      - Límite global por IP 
      - Mensaje en el último intento
    """

    # Configurables desde settings.py
    ATTEMPTS_LIMIT = getattr(settings, "LOGIN_ATTEMPTS_LIMIT", 3)
    LOCKOUT_SECONDS = getattr(settings, "LOGIN_LOCKOUT_SECONDS", 3600)  # 1 hora

    # Protección secundaria por IP
    IP_ATTEMPTS_LIMIT = getattr(settings, "LOGIN_IP_ATTEMPTS_LIMIT", 30)
    IP_ATTEMPTS_WINDOW_SECONDS = getattr(settings, "LOGIN_IP_WINDOW_SECONDS", 600)  # 10 min
    IP_BLOCK_SECONDS = getattr(settings, "LOGIN_IP_BLOCK_SECONDS", 3600)  # 1 hora

    def _keys(self, username, ip):
        base = f"login:{username}:{ip}"
        return f"{base}:attempts", f"{base}:lock_until"

    def clean(self):
        username = (self.data.get("username") or "").strip()
        password = self.data.get("password") or ""
        ip = _client_ip(self.request)
        now = timezone.now()

        # ---- Bloqueo global por IP ----
        ip_block_key = f"login:ip:{ip}:blocked_until"
        ip_block_until = cache.get(ip_block_key)
        if ip_block_until and ip_block_until > now:
            mins = int((ip_block_until - now).total_seconds() // 60) or 1
            raise forms.ValidationError(
                f"Demasiados intentos desde tu red. Intenta nuevamente en ~{mins} minutos."
            )

        # ---- Contador por usuario+IP ----
        attempts_key, lock_key = self._keys(username or "-", ip)
        lock_until = cache.get(lock_key)
        if lock_until and lock_until > now:
            mins = int((lock_until - now).total_seconds() // 60) or 1
            raise forms.ValidationError(
                f"Tu cuenta está bloqueada. Podrás intentarlo nuevamente en ~{mins} minutos."
            )

        # ---- Contador global por IP (spray protection) ----
        ip_attempts_key = f"login:ip:{ip}:attempts"
        ip_attempts = cache.get(ip_attempts_key, 0) + 1
        cache.set(ip_attempts_key, ip_attempts, self.IP_ATTEMPTS_WINDOW_SECONDS)
        if ip_attempts >= self.IP_ATTEMPTS_LIMIT:
            cache.set(ip_block_key, now + timedelta(seconds=self.IP_BLOCK_SECONDS), self.IP_BLOCK_SECONDS)
            cache.delete(ip_attempts_key)
            raise forms.ValidationError(
                "Se detectaron demasiados intentos desde tu red. Acceso bloqueado por 1 hora."
            )

        # ---- Intento de autenticación ----
        user = authenticate(self.request, username=username, password=password)
        if user is None:
            attempts = cache.get(attempts_key, 0) + 1
            cache.set(attempts_key, attempts, self.LOCKOUT_SECONDS)

            remaining = self.ATTEMPTS_LIMIT - attempts
            if remaining <= 0:
                cache.set(lock_key, now + timedelta(seconds=self.LOCKOUT_SECONDS), self.LOCKOUT_SECONDS)
                cache.delete(attempts_key)
                raise forms.ValidationError(
                    "Has excedido los 3 intentos. Tu cuenta queda bloqueada por 1 hora."
                )
            elif remaining == 1:
                raise forms.ValidationError(
                    "Usuario o contraseña incorrectos. ¡Último intento! "
                    "Si vuelves a fallar, no podrás intentarlo hasta dentro de una hora."
                )
            else:
                raise forms.ValidationError(
                    f"Usuario o contraseña incorrectos. Te quedan {remaining} intentos."
                )

        # ---- Éxito: limpia contadores ----
        cache.delete(attempts_key)
        cache.delete(lock_key)
        self.user_cache = user
        self.confirm_login_allowed(user)
        return self.cleaned_data
