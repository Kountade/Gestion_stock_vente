from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Livraison, Produit, Categorie ,CommandeApprovisionnement,Profile, User
from application import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


# Activer une catégorie lorsqu'un produit y est associé
@receiver(post_save, sender=Produit)
def activer_categorie_si_produit_associe(sender, instance, **kwargs):
    categorie = instance.categorie
    if categorie and not categorie.actif:  # Si la catégorie est inactive
        categorie.actif = True
        categorie.save()

# Désactiver une catégorie lorsqu'elle n'a plus de produits
@receiver(post_delete, sender=Produit)
def desactiver_categorie_si_plus_de_produits(sender, instance, **kwargs):
    categorie = instance.categorie
    if categorie and categorie.produits.count() == 0:  # Si plus aucun produit
        categorie.actif = False
        categorie.save()

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Stock





@receiver(post_save, sender=Livraison)
def update_stock_on_livraison(sender, instance, created, **kwargs):
    if created:  # Lorsque la livraison est créée
        commande = instance.produit  # Récupérer la commande associée à la livraison
        produit = commande.produit.produit  # Récupérer le produit via la commande
        if produit:
            stock = produit.stock  # Récupérer le stock du produit
            if stock and stock.quantite >= instance.quantite_commande:
                stock.quantite -= instance.quantite_commande  # Réduire la quantité en stock
                stock.save()  # Sauvegarder les modifications du stock
            else:
                # Si le stock est insuffisant, vous pouvez gérer cette situation ici
                print("Stock insuffisant pour la livraison.")
                


@receiver(pre_save, sender=CommandeApprovisionnement)
def handle_commande_cancellation(sender, instance, **kwargs):
    if instance.pk:  # Si l'objet est déjà dans la base
        previous_instance = CommandeApprovisionnement.objects.get(pk=instance.pk)
        if previous_instance.statut != instance.statut and instance.statut == 'annulee':
            # Annuler la commande, remettre à jour le stock
            produit = instance.produit.produit
            if produit:
                stock = produit.stock
                stock.quantite -= instance.quantite  # Remettre le stock à jour
                stock.save()




@receiver(pre_save, sender=Livraison)
def recalculate_totals_on_livraison(sender, instance, **kwargs):
    # S'assurer que les totaux sont recalculés avant d'enregistrer
    if instance.prix_unitaire and instance.quantite_commande and instance.prix_transport:
        instance.total = instance.prix_unitaire * instance.quantite_commande
        instance.total_global = instance.total + instance.prix_transport



from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CommandeApprovisionnement, Livraison

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Livraison, CommandeApprovisionnement, Stock

# Mise à jour du statut de la commande associée siganls qui mache
@receiver(post_save, sender=Livraison)
def update_commande_and_stock(sender, instance, created, **kwargs):
    if created:  # Si une nouvelle livraison a été créée
        # Mise à jour du statut de la commande associée
        commande = instance.produit
        if commande:
            commande.statut = 'livree'
            commande.save()

            # Mise à jour de la quantité dans le stock du produit
            stock = commande.produit  # Accès au Stock via la commande
            stock.quantite += instance.quantite_commande
            stock.save()



# Mise à jour du statut de la commande associée siganls qui mache

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Livraison, CommandeApprovisionnement

@receiver(post_save, sender=Livraison)
def update_commande_status(sender, instance, created, **kwargs):
    """
    Met à jour le statut de la commande associée lorsqu'une livraison est enregistrée.
    """
    if created:  # Si une nouvelle livraison est créée
        commande = instance.produit  # La commande associée via la clé étrangère
        if commande.livraisons_produit.exists():  # Vérifie s'il existe des livraisons associées
            commande.statut = 'livree'
        else:
            commande.statut = 'en_cours'
        commande.save()




from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import VenteProduit, Stock

@receiver(post_save, sender=VenteProduit)
def mettre_a_jour_stock_vente(sender, instance, created, **kwargs):
    """
    Mettre à jour le stock lors de la création ou modification d'une vente produit.
    """
    produit = instance.produit
    stock = produit.stock

    # Assurez-vous que les quantités sont des entiers
    quantite_stock = int(stock.quantite)  # Conversion explicite
    quantite_vente = int(instance.quantite)  # Conversion explicite

    if created:
        # Réduire le stock pour une nouvelle vente
        stock.quantite = quantite_stock - quantite_vente
    else:
        # Ajouter un contrôle supplémentaire si la logique nécessite un ajustement
        stock.quantite = quantite_stock - quantite_vente

    stock.save()



@receiver(post_delete, sender=VenteProduit)
def remettre_a_jour_stock_vente_suppression(sender, instance, **kwargs):
    """
    Ce signal est déclenché après la suppression d'un produit dans une vente.
    Il remet à jour la quantité en stock du produit supprimé.
    """
    produit = instance.produit
    stock = produit.stock  # Récupérer le stock du produit
    stock.quantite += instance.quantite  # Ajouter la quantité supprimée au stock
    stock.save()



    from django.db.models.signals import post_save
    from django.contrib.auth.models import User
    from django.dispatch import receiver
    from .models import Profile
    


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(staff=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
