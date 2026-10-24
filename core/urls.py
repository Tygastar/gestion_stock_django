from django.urls import path
from . import views

urlpatterns = [
    path("", views.Accueil.as_view(), name="accueil"),
    path("basculer/<int:user_id>", views.basculer, name="basculer"),
]

for m in views.MODELES:
    n = views.nom(m)
    urlpatterns += [
        path(f"{n}/", views.Liste.as_view(model=m), name=f"{n}_liste"),
        path(f"{n}/ajouter/", views.Creer.as_view(model=m), name=f"{n}_ajouter"),
        path(f"{n}/<str:pk>/modifier/", views.Modifier.as_view(model=m), name=f"{n}_modifier"),
        path(f"{n}/<str:pk>/supprimer/", views.Supprimer.as_view(model=m), name=f"{n}_supprimer"),
    ]