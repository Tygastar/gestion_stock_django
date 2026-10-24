from django.contrib.auth import get_user_model


def menu_utilisateurs(request):
    u = request.user
    if not u.is_authenticated:
        return {}
    maitre_id = request.session.get("maitre_id")
    est_maitre = u.is_superuser or bool(maitre_id)
    ctx = {
        "est_maitre": est_maitre,
        "en_bascule": bool(maitre_id) and not u.is_superuser,
    }
    if est_maitre:
        ctx["comptes"] = (
            get_user_model().objects.filter(is_active=True)
            .order_by("username")
        )
    return ctx