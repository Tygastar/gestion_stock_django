from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Sum  

class Fournisseur(models.Model):
    idFournisseur = models.AutoField(primary_key=True, db_column='IdFounisseur')
    NomFournisseur = models.CharField(max_length=100,null=False, db_column='NomFournisseur')
    AdresseFournisseur = models.CharField(max_length=225,null=False, db_column='AdresseFournisseur')
    Tel_Fournisseur = models.CharField(max_length=45,null=False, db_column='Tel_Fournisseur')
    EmailFournisseur = models.CharField(max_length=100,null=False, db_column='Email_Fournisseur')

    class Meta:
        db_table = 'fournisseur'
    def __str__(self):
        return f"{self.NomFournisseur} {self.Tel_Fournisseur}"
class Utilisateur(models.Model):
    idUtilisateur = models.AutoField(primary_key=True, db_column='IdUtilisateur')
    NomUtilisateur = models.CharField(max_length=100,null=False, db_column='NomUtilisateur')
    Poste = models.CharField(max_length=45, null=False, db_column='Poste')
    Log_In = models.CharField(max_length=45, null=False, unique=True, db_column='Log_In')
    class Meta:
        db_table = 'utilisateur'

    def __str__(self):
        return f"{self.NomUtilisateur} {self.Poste}"

class BonCommande(models.Model):
    idCommande = models.AutoField(primary_key=True, db_column='IdCommande')
    Date_Commande = models.DateTimeField(auto_now_add=True, db_column='Date_Commande')
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, db_column='IdFournisseur')
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, db_column='IdUtilisateur')
    class Meta:
        db_table = 'bon_commande'
    def __str__(self):
        return f"BC-{self.idCommande}"

class Categorie(models.Model):
    idCategorie = models.AutoField(primary_key=True, db_column='IdCategorie')
    NomCategorie = models.CharField(max_length=100, null=False, db_column='NomCategorie')
    Description = models.TextField(blank=True, null=True,db_column='Description')
    class Meta:
        db_table = 'categorie'
    def __str__(self):
        return self.NomCategorie

class Produit(models.Model):
    idProduit = models.AutoField(primary_key=True, db_column='IdProduit')
    NomProduit = models.CharField(max_length=100, null=False, db_column='NomProduit')
    Description_produit = models.TextField(blank=True, null=True, db_column='Description_produit')
    Prix_Unitaire = models.DecimalField(max_digits=10, decimal_places=2, db_column='Prix_Unitaire')
    Seuil = models.IntegerField(default=5, db_column='Seuil')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, db_column='IdCategorie')
    class Meta:
        db_table = 'produit'
    def __str__(self):
        return self.NomProduit

class LigneCommande(models.Model):
    bon_commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, db_column='IdCommande')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, db_column='IdProduit')
    Quantite_Produit = models.IntegerField(null=False, db_column='Quantite_Produit')
    Prix_Achat = models.DecimalField(max_digits=10, decimal_places=2, null=False, db_column='Prix_Achat')
    class Meta:
        db_table = 'ligne_commande'
        unique_together = (('bon_commande', 'produit'),)
    def __str__(self):
        return f"{self.bon_commande}-{self.produit}"

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('ENTREE', 'Entree'),
        ('SORTIE', 'Sortie'),
    ]
    idMouvementStock = models.AutoField(primary_key=True, db_column='IdMouvementStock')
    Type_mouvement = models.CharField(max_length=10, choices=TYPE_CHOICES, db_column='Type_mouvement')
    idProduit = models.ForeignKey(Produit, on_delete=models.CASCADE, db_column='IdProduit')
    Qte_Produit_Movt = models.IntegerField(null=False,db_column='Qte_Produit_Movt')
    Date_Movt = models.DateTimeField(auto_now_add=True, db_column='Date_Movt')
    idUtilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, db_column='IdUtilisateur')
    class Meta:
        db_table = 'mouvementstock'
    def __str__(self):
        return f"{self.Type_mouvement}-{self.idProduit}"
    def clean(self):
        if not self._state.adding:
            raise ValidationError(
                "Un mouvement enregistre ne peut pas etre modifier."
                "Creez un mouvement correctif a la place."
            )
        if self.Qte_Produit_Movt is None:
            return
        if self.Qte_Produit_Movt <= 0:
            raise ValidationError("La quantité doit être supérieure à 0.")
        if (self._state.adding and self.Type_mouvement == "SORTIE"
                and self.idProduit_id):
            dispo = Stock.objects.filter(
                idProduit=self.idProduit_id
            ).aggregate(t=Sum("Qte_Produit_Dispo"))["t"] or 0
            if self.Qte_Produit_Movt > dispo:
                raise ValidationError(
                    f"Stock insuffisant : {dispo} disponible(s).")

    def save(self, *args, **kwargs):
        if not self._state.adding:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            lignes = list(
                Stock.objects.select_for_update()
                .filter(idProduit=self.idProduit_id)
                .order_by("idStock")
            )
            if self.Type_mouvement == "ENTREE":
                if lignes:
                    lignes[0].Qte_Produit_Dispo += self.Qte_Produit_Movt
                    lignes[0].save()
                else:
                    Stock.objects.create(
                        idProduit=self.idProduit,
                        emplacement="Principal",
                        Qte_Produit_Dispo=self.Qte_Produit_Movt,
                    )
            else:
                reste = self.Qte_Produit_Movt
                if reste > sum(l.Qte_Produit_Dispo for l in lignes):
                    raise ValidationError("Stock insuffisant.")
                for ligne in lignes:
                    pris = min(ligne.Qte_Produit_Dispo, reste)
                    ligne.Qte_Produit_Dispo -= pris
                    ligne.save()
                    reste -= pris
                    if reste == 0:
                        break
            return super().save(*args, **kwargs)

class Stock(models.Model):
    idStock = models.AutoField(primary_key=True, db_column='IdStock')
    idProduit = models.ForeignKey(Produit, on_delete=models.CASCADE, db_column='IdProduit')
    emplacement = models.CharField(max_length=10, null=False, db_column='Emplacement')
    Qte_Produit_Dispo = models.IntegerField(
        validators=[MinValueValidator(0, message="le stock ne peut jamais etre negatif")],
        db_column='Qte_Produit_Dispo'
    )             
    class Meta:
        db_table = 'stock'
        constraints = [
            models.CheckConstraint(condition=models.Q(Qte_Produit_Dispo__gte=0), name='stock_non_negatif')
        ]
    def __str__(self):
        return f"{self.idProduit}-{self.Qte_Produit_Dispo}"