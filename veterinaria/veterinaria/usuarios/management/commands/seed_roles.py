from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import Usuario, VeterinarioPerfil
from servicios.models import Servicio
from citas.models import Cita

class Command(BaseCommand):
    help = "Crea grupos y asigna permisos base para cliente, veterinario y admin."

    def handle(self, *args, **options):
        grupos = {
            'cliente': [],
            'veterinario': [],
            'administrador': ['add_*', 'change_*', 'delete_*', 'view_*']
        }

        # Permisos para veterinario (afina según tu necesidad)
        perms_vet = []
        # ver/editar su perfil (modelo VeterinarioPerfil)
        ct_perfil = ContentType.objects.get_for_model(VeterinarioPerfil)
        perms_vet += list(Permission.objects.filter(content_type=ct_perfil))

        # ver/modificar Cita (luego limitaremos por lógica en vistas)
        ct_cita = ContentType.objects.get_for_model(Cita)
        perms_vet += list(Permission.objects.filter(content_type=ct_cita, codename__startswith=('view_', 'change_')))

        # cambiar disponibilidad de Servicio
        ct_serv = ContentType.objects.get_for_model(Servicio)
        perms_vet += list(Permission.objects.filter(content_type=ct_serv, codename__startswith=('view_', 'change_')))

        # Crear/obtener grupos
        g_cliente, _ = Group.objects.get_or_create(name='cliente')
        g_vet, _ = Group.objects.get_or_create(name='veterinario')
        g_admin, _ = Group.objects.get_or_create(name='administrador')

        # Asignar permisos
        g_vet.permissions.set(set(perms_vet))

        # Admin: todos los permisos
        all_perms = Permission.objects.all()
        g_admin.permissions.set(all_perms)

        self.stdout.write(self.style.SUCCESS("Grupos y permisos iniciales configurados."))
