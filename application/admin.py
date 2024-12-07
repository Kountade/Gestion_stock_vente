from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape
from django.urls import reverse

from django.contrib import admin
from .models import Produit
from django.utils.html import format_html


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix', 'actif', 'image_preview')
    list_filter = ('actif', 'categorie')
    search_fields = ('nom', 'description')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;"/>', obj.image.url)
        return "Pas d'image"
    image_preview.short_description = 'Aperçu'



from django.contrib import admin
from .models import Profile
from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('staff', 'address', 'telephone', 'firstname', 'lastname', 'tache', 'image')
    search_fields = ('staff__username', 'address', 'telephone')
    list_filter = ('staff',)
    ordering = ('staff',)

admin.site.register(Profile, ProfileAdmin)

from django.contrib import admin
from .models import Client, Vente, VenteProduit

# Pour personnaliser l'affichage dans l'admin
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'telephone', 'ville', 'pays', 'date_creation')
    search_fields = ('nom', 'prenom', 'email')
    list_filter = ('ville', 'pays')

class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date', 'statut_paiement', 'total')
    search_fields = ('client__nom', 'client__prenom', 'client__email')
    list_filter = ('statut_paiement', 'date')
    readonly_fields = ('total',)  # Le champ 'total' est en lecture seule

class VenteProduitAdmin(admin.ModelAdmin):
    list_display = ('vente', 'produit', 'quantite', 'prix_unitaire')
    search_fields = ('produit__nom',)
    list_filter = ('vente',)

# Enregistrement des modèles avec leurs classes Admin respectives
admin.site.register(Client, ClientAdmin)
admin.site.register(Vente, VenteAdmin)
admin.site.register(VenteProduit, VenteProduitAdmin)
