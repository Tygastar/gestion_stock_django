from django.contrib import admin
from .models import Fournisseur, Utilisateur, BonCommande, Categorie, Produit, LigneCommande, MouvementStock, Stock

admin.site.register(Fournisseur)
admin.site.register(Utilisateur)
admin.site.register(BonCommande)
admin.site.register(Categorie)
admin.site.register(Produit)
admin.site.register(LigneCommande)
admin.site.register(MouvementStock)
admin.site.register(Stock)