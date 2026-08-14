from core.models import AuditLog


def create_audit_log(
    *,
    user,
    action,
    instance,
):
    """
    Crea un registro de auditoría para una acción realizada
    sobre una instancia del sistema.
    """

    if user is not None:
        username = user.username

        full_name = user.get_full_name().strip()

        if full_name:
            user_name = full_name
        else:
            user_name = user.username

    else:
        username = "Sistema"
        user_name = "Sistema"

    AuditLog.objects.create(
        user=user,
        username=username,
        user_name=user_name,
        entity_name=instance.__class__.__name__,
        entity_id=instance.pk,
        action=action,
    )