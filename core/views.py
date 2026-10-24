from django.contrib.auth import get_user_model, login
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, TemplateView)
from . import models

MODELES = [
    models.Categorie, models.Fournisseur, models.Produit, models.Stock,
    models.BonCommande, models.LigneCommande, models.MouvementStock,
    models.Utilisateur,
]

def nom(m):
    return m._meta.model_name

def perm(m, action):
    return f"{m._meta.app_label}.{action}_{m._meta.model_name}"


class Accueil(LoginRequiredMixin, TemplateView):
    template_name = "core/accueil.html"

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        u = self.request.user
        ctx["tables"] = [
            (m._meta.verbose_name_plural.title(), reverse(f"{nom(m)}_liste"))
            for m in MODELES
            if u.has_perm(perm(m, "view"))
        ]
        ctx["alertes"] = []
        if u.has_perm(perm(models.Stock, "view")):
            ctx["alertes"] = (
                models.Produit.objects
                .annotate(total=Coalesce(Sum("stock__Qte_Produit_Dispo"), 0))
                .filter(total__lte=F("Seuil"))
                .order_by("total")
            )
        return ctx


class Droit(PermissionRequiredMixin):
    action = "view"

    def get_permission_required(self):
        return [perm(self.model, self.action)]


class Liste(Droit, ListView):
    template_name = "core/liste.html"
    action = "view"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().order_by("pk")
        q = self.request.GET.get("q", "").strip()
        if q:
            filtre = Q()
            for f in self.model._meta.fields:
                if f.get_internal_type() in ("CharField", "TextField"):
                    filtre |= Q(**{f"{f.name}__icontains": q})
            qs = qs.filter(filtre)
        return qs

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        u = self.request.user
        n = nom(self.model)
        champs = self.model._meta.fields
        peut_modifier = u.has_perm(perm(self.model, "change"))
        peut_supprimer = u.has_perm(perm(self.model, "delete"))
        ctx["q"] = self.request.GET.get("q", "")
        ctx["titre"] = self.model._meta.verbose_name_plural.title()
        ctx["entetes"] = [f.verbose_name.title() for f in champs]
        ctx["url_ajouter"] = (
            reverse(f"{n}_ajouter") if u.has_perm(perm(self.model, "add")) else None
        )
        ctx["lignes"] = [
            {
                "valeurs": [getattr(o, f.name) for f in champs],
                "modifier": reverse(f"{n}_modifier", args=[o.pk]) if peut_modifier else None,
                "supprimer": reverse(f"{n}_supprimer", args=[o.pk]) if peut_supprimer else None,
            }
            for o in ctx["object_list"]
        ]
        return ctx
def utilisateur_connecte(request):
    return models.Utilisateur.objects.filter(
        NomUtilisateur__iexact=request.user.username).first()
        
class PageMixin:
    def get_success_url(self):
        return reverse(f"{nom(self.model)}_liste")

    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        ctx["titre"] = self.model._meta.verbose_name.title()
        ctx["url_liste"] = self.get_success_url()
        return ctx
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.model is models.MouvementStock:
            form.fields.pop("idUtilisateur", None)
        return form

class Creer(Droit, PageMixin, CreateView):
    template_name = "core/form.html"
    fields = "__all__"
    action = "add"
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)
        if self.model is models.MouvementStock:
            ctx["enregistre_par"] = utilisateur_connecte(self.request)
        return ctx
    def form_valid(self, form):
        if self.model is models.MouvementStock:
            auteur = utilisateur_connecte(self.request)
            if auteur is None:
                form.add_error(
                    None,
                    "Votre compte n'est lie a aucun utilisateur"
                    "contactez l'administrateur."
                )
                return self.form_invalid(form)
            form.instance.idUtilisateur = auteur
        return super().form_valid(form)

class Modifier(Droit, PageMixin, UpdateView):
    template_name = "core/form.html"
    fields = "__all__"
    action = "change"


class Supprimer(Droit, PageMixin, DeleteView):
    template_name = "core/confirmer.html"
    action = "delete"
#@require_POST
def basculer(request, user_id):
    Compte = get_user_model()
    maitre_id = request.session.get("maitre_id")
    if request.user.is_authenticated and request.user.is_superuser:
        maitre_id = request.user.pk
    maitre = None
    if maitre_id:
        maitre = Compte.objects.filter(pk=maitre_id, is_superuser=True).first()
    if maitre is None:
        raise PermissionDenied
    cible = get_object_or_404(Compte, pk=user_id, is_active=True)
    login(request, cible,
          backend="django.contrib.auth.backends.ModelBackend")
    if cible.pk != maitre.pk:
        request.session["maitre_id"] = maitre.pk
    return redirect("accueil") 
