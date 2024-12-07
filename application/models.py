import datetime
from django.db import models
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# Create your models here.
from django.db import models

from django.contrib.auth.models import AbstractUser, Group, Permission



class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    actif = models.BooleanField(choices=[(True, 'Actif'), (False, 'Inactif')], default=False)
    
    def __str__(self):
        return self.nom

    def activer_si_produit(self):
        """Met à jour la catégorie en 'actif' si un produit est associé."""
        if self.produits.filter(actif=True).exists():
            self.actif = True
            self.save()

from django.db import models
from django.db.models import Q

class Produit(models.Model):
    # Vos champs existants
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE, related_name='produits')
    actif = models.BooleanField(choices=[(True, 'Disponible'), (False, 'Indisponible')], default=False)
    image = models.ImageField(upload_to='produits/', blank=True, null=True)

    def __str__(self):
        return self.nom

    def ajouter_stock(self, quantite):
        stock = self.stock  # Utilise le related_name défini
        if stock:
            stock.quantite += quantite
            stock.save()
        else:
            Stock.objects.create(produit=self, quantite=quantite)

    @staticmethod
    def produits_disponibles():
        """Retourne les produits dont le stock est supérieur à 0"""
        return Produit.objects.filter(
            actif=True,
            stock__quantite__gt=0
        )

    def mettre_actif_si_categorie(self):
        if self.categorie.actif:
            self.actif = True
            self.save()


class Stock(models.Model):
    STATUT_CHOICES = [
        ('en_stock', 'En stock'),
        ('rupture', 'Rupture'),
        ('en_approvisionnement', 'En approvisionnement'),
        ('reserve', 'Réservé'),
    ]
    EMPLACEMENT_CHOICES = [
        ('entrepot_1', 'Entrepôt 1'),
        ('entrepot_2', 'Entrepôt 2'),
        ('magasin', 'Magasin'),
        ('reserve', 'Réserve'),
        ('autre', 'Autre'),
    ]
    produit = models.OneToOneField(Produit, on_delete=models.CASCADE, related_name='stock')
    emplacement = models.CharField(max_length=50, choices=EMPLACEMENT_CHOICES, default='entrepot_1')
    quantite = models.PositiveIntegerField(default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_stock')  # Statut du stock
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Stock de {self.produit.nom} - {self.quantite} unités"





######################################################################################################################


class Fournisseur(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    telephone = models.CharField(max_length=15, null=True, blank=True)
    adresse = models.TextField(null=True, blank=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom


class CommandeApprovisionnement(models.Model):
 
    produit = models.ForeignKey(Stock, related_name='commandes', on_delete=models.CASCADE)

   
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE, related_name="commandes")
   
    date_commande = models.DateField(verbose_name="Date de Commande",null=False,  # Si vous souhaitez qu'il reste obligatoire
        blank=False,  # Empêche les champs vides dans les formulaires
        default=datetime.date.today  # Fournit une valeur par défaut (optionnel)
    )
    quantite = models.PositiveIntegerField()
    statut = models.CharField(max_length=50, choices=[('en_cours', 'En Cours'), ('livree', 'Livrée')], default='en_cours')
    commentaire = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Commande de {self.produit.produit.nom} ({self.quantite} unités) du fournisseur {self.fournisseur}"
    
from datetime import timedelta


from decimal import Decimal, InvalidOperation

class Livraison(models.Model):
    produit = models.ForeignKey(CommandeApprovisionnement, on_delete=models.CASCADE, related_name='livraisons_produit') 
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix Unitaire")
    quantite_commande = models.PositiveIntegerField(verbose_name="Quantité Commandée")
    moyen_transport = models.CharField(max_length=100, verbose_name="Moyen de Transport")
    prix_transport = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix du Transport")
    date_livraison = models.DateField(verbose_name="Date de Livraison")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total", default=0)
    total_global = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Global", default=0)
    difference_jours = models.IntegerField(verbose_name="Différence en jours", default=0)

    def save(self, *args, **kwargs):
        try:
            # Vérification et impression des valeurs avant les calculs
            print(f"prix_unitaire: {self.prix_unitaire}, quantite_commande: {self.quantite_commande}, prix_transport: {self.prix_transport}")

            if self.prix_unitaire is None or self.quantite_commande is None or self.prix_transport is None:
                raise ValueError("Les champs prix unitaire, quantité commandée et prix transport doivent être définis.")

            # Calcul du total (prix unitaire * quantité commandée)
            self.total = Decimal(self.prix_unitaire) * Decimal(self.quantite_commande)
            
            # Calcul du total global (total + prix transport)
            self.total_global = self.total + Decimal(self.prix_transport)
        except (InvalidOperation, ValueError) as e:
            # En cas d'erreur, gérer l'exception et afficher l'erreur
            print(f"Erreur lors du calcul des totaux : {e}")
            self.total = Decimal(0)
            self.total_global = Decimal(0)

        # Calcul de la différence de jours si date de livraison et commande existent
        commande_approvisionnement = self.get_commande_approvisionnement()
        if self.date_livraison and commande_approvisionnement:
            self.difference_jours = (self.date_livraison - commande_approvisionnement.date_commande).days

        # Obtention du fournisseur lié au produit via la commande
        self.fournisseur = self.get_fournisseur_from_produit()
        
        # Sauvegarde de l'objet
        super(Livraison, self).save(*args, **kwargs)

    def get_commande_approvisionnement(self):
        """Retourne la commande d'approvisionnement associée au produit de la livraison"""
        return self.produit  # 'produit' est une clé étrangère vers 'CommandeApprovisionnement'

    def get_fournisseur_from_produit(self):
        """Retourne le fournisseur associé au produit via la commande d'approvisionnement"""
        commande = self.get_commande_approvisionnement()
        if commande:
            return commande.fournisseur
        return None

    def __str__(self):
        produit_nom = self.produit.produit.nom if self.produit and self.produit.produit else "Produit inconnu"
        return f"Livraison du produit {produit_nom}"



class Client(models.Model):
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    email = models.EmailField(unique=True, verbose_name="Email")
    telephone = models.CharField(max_length=15, verbose_name="Téléphone")
    adresse = models.TextField(verbose_name="Adresse", blank=True, null=True)
    ville = models.CharField(
        max_length=50, verbose_name="Ville", blank=True, null=True)
    pays = models.CharField(
        max_length=50, verbose_name="Pays", blank=True, null=True)
    code_postal = models.CharField(
        max_length=10, verbose_name="Code Postal", blank=True, null=True)
    date_creation = models.DateTimeField(
        auto_now_add=True, verbose_name="Date de Création")

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} {self.prenom}"





class Vente(models.Model):
    STATUT_PAIEMENT_CHOICES = [
        ('payee', 'Payée'),
        ('non_payee', 'Non Payée'),
    ]
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='ventes')
    date = models.DateTimeField(auto_now_add=True)
    statut_paiement = models.CharField(
        max_length=10,
        choices=STATUT_PAIEMENT_CHOICES,
        default='non_payee',
        verbose_name=_("Statut Paiement")
    )

    def __str__(self):
        return f"Vente {self.id} - {self.client.nom} {self.client.prenom}"

    def total(self):
        """Calcule le total de la vente en fonction des produits et de leur quantité."""
        return sum([vp.quantite * vp.prix_unitaire for vp in self.ventes_produits.all()])


class VenteProduit(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name="ventes_produits")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.produit.nom} (x{self.quantite})"




class Employe(models.Model):
    ROLES = [
        ('ADMIN', 'Administrateur'),
        ('VENDEUR', 'Vendeur'),
        ('OVRIER', 'Ouvrier'),
        ('JOURNALIER', 'Journalier'),
    ]

    STATUTS = [
        (True, 'Actif'),
        (False, 'Inactif'),
    ]

    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='VENDEUR')
    telephone = models.CharField(max_length=15, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    date_embauche = models.DateField()
    actif = models.BooleanField(choices=STATUTS, default=False)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.role}"




TYPE_CONTRAT = [
    ('CDI', 'Contrat à durée indéterminée'),
    ('CDD', 'Contrat à durée déterminée'),
    ('Freelance', 'Freelance'),
    ('Stage', 'Stage'),
]


class Contrat(models.Model):
    employe = models.ForeignKey(
        Employe, on_delete=models.CASCADE, related_name='contrats')
    type_contrat = models.CharField(max_length=20, choices=TYPE_CONTRAT)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employe.nom} - {self.type_contrat}"


class Rapport(models.Model):
    titre = models.CharField(max_length=100)
    contenu = models.TextField()
    date_rapport = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titre
    

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    staff = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    telephone = models.CharField(max_length=50)
    firstname = models.CharField(max_length=50, blank=True, null=True)
    lastname = models.CharField(max_length=50, blank=True, null=True)
    tache = models.TextField(max_length=2000, blank=True, null=True)
   
    image = models.ImageField(default='default.png',
                              upload_to='profile_images')

    def __str__(self):
        return f'{self.staff.username}-Profile  - {self.firstname} {self.lastname}'
