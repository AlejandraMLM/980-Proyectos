from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplica el valor por el argumento."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter(name="getitem")
def getitem(d, key):
    """
    Permite usar {{ form|getitem:'vet_3' }} y también en errores:
    {{ form.errors|getitem:'vet_3' }}
    """
    try:
        return d[key]
    except Exception:
        return None
