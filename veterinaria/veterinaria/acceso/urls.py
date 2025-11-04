from django.urls import path
from .views import LockoutLoginView, redirigir_por_rol

app_name = "acceso"

urlpatterns = [
    path("login/", LockoutLoginView.as_view(), name="login"),
    path("redir/", redirigir_por_rol, name="redir_por_rol"),
]
