# usuarios/context_processors.py
def veterinarios_disponibles(request):
    """
    Expone en todas las plantillas la lista 'veterinarios'
    con solo veterinarios disponibles.
    Soporta dos esquemas:
      - Modelo VeterinarioPerfil(disponible, foto, usuario, especialidades, bio, servicios M2M)
      - Solo Usuario(tipo_usuario='veterinario', disponible?, foto?)
    """
    try:
        from usuarios.models import VeterinarioPerfil  # tu perfil, si existe
        qs = (VeterinarioPerfil.objects
              .filter(disponible=True)
              .select_related('usuario')
              .prefetch_related('servicios')
              .order_by('usuario__first_name', 'usuario__last_name'))
        return {"veterinarios": qs}
    except Exception:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            # Si tu modelo Usuario tiene campo 'disponible', úsalo. Si no, quita el filtro.
            qs = (User.objects
                  .filter(tipo_usuario='veterinario')
                  .order_by('first_name', 'last_name'))
            # No podemos garantizar 'disponible' aquí, pero al menos listamos veterinarios.
            return {"veterinarios": qs}
        except Exception:
            return {"veterinarios": []}
