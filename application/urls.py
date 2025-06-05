from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


from . import views

urlpatterns = [
    path("home", views.home, name='home'),
    # categories
   path('categories/', views.liste_categories, name='liste_categories'),
   path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
   path('categories/modifier/<int:pk>/', views.modifier_categorie, name='modifier_categorie'),
    path('supprimer/<int:pk>/', views.supprimer_categorie, name='supprimer_categorie'),

    # Produits
    path('exporter-excel/', views.exporter_excel, name='exporter_excel'),
    path('exporter-pdf/', views.generer_pdf, name='exporter_pdf'),
    path('produits/', views.liste_produits, name='liste_produits'),
    path('produit/ajouter/', views.ajouter_produit, name='ajouter_produit'),
    path('produit/modifier/<int:pk>/', views.modifier_produit, name='modifier_produit'),
    path('produits/supprimer/<int:pk>/',views.supprimer_produit, name='supprimer_produit'),
    
     # Stock
    path('stocks/', views.liste_stocks, name='liste_stocks'),
    path('stocks/ajouter/', views.ajouter_stock, name='ajouter_stock'),
    path('stocks/modifier/<int:pk>/', views.modifier_stock, name='modifier_stock'),
    path('stocks/supprimer/<int:pk>/', views.supprimer_stock, name='supprimer_stock'),
    # fourniseurs

    path('fournisseurs/', views.liste_fournisseurs, name='liste_fournisseurs'),
    path('fournisseurs/ajouter/', views.ajouter_fournisseur,
         name='ajouter_fournisseur'),
    path('fournisseurs/modifier/<int:pk>/',
         views.modifier_fournisseur, name='modifier_fournisseur'),
    path('fournisseurs/supprimer/<int:pk>/',
         views.supprimer_fournisseur, name='supprimer_fournisseur'),
     # Commande
    
    path('liste_commandes/', views.liste_commandes, name='liste_commandes'),  # 
    path('ajouter_commande/', views.ajouter_commande, name='ajouter_commande'),
     path('commande/<int:pk>/modifier/', views.modifier_commande, name='modifier_commande'),
    path('commande/<int:pk>/supprimer/', views.supprimer_commande, name='supprimer_commande'),
    
    # Livrasion
     # Page d'accueil
    path('livraison/', views.liste_livraisons, name='liste_livraisons'),  # Liste des livraisons
    path('livraison/create/', views.enregistrer_livraison, name='enregistrer_livraison'),  # Créer une livraison
    path('livraison/<int:pk>/', views.details_livraison, name='details_livraison'), 
    # Détails d'une livraison
    path('livraison/<int:pk>/update/', views.modifier_livraison, name='modifier_livraison'),  # Modifier une livraison
    path('livraison/<int:pk>/delete/', views.supprimer_livraison, name='supprimer_livraison'),  # Supprimer une livraison
     path('livraison/pdf/<int:livraison_id>/', views.generate_delivery_note_pdf, name='generate_delivery_note_pdf'),

    # clients
    path('clients/', views.liste_clients, name='liste_clients'),
    path('clients/ajouter/', views.ajouter_client, name='ajouter_client'),
    path('clients/modifier/<int:pk>/',
         views.modifier_client, name='modifier_client'),
    path('clients/supprimer/<int:pk>/',
         views.supprimer_client, name='supprimer_client'),
    
      # ventes
    path('ajouter-vente/', views.ajouter_vente, name='ajouter_vente'),  # Ajouter une nouvelle vente
    path('liste-ventes/', views.liste_ventes, name='liste_ventes'),    # Voir la liste des ventes
    path('detail-vente/<int:pk>/', views.detail_vente, name='detail_vente'),
    
    path('ventes/modifier/<int:pk>/', views.modifier_vente, name='modifier_vente'),
    path('vente/<int:pk>/supprimer/', views.supprimer_vente, name='supprimer_vente'),
    path('vente/pdf/<int:vente_id>/', views.generate_delivery_vente_pdf, name='generate_delivery_vente_pdf'),
    # urls.py
    path("ticket/vente/<int:vente_id>/", views.generer_ticket_pdf, name="generer_ticket_pdf"),

     path('send_invoice_email/', views.send_invoice_email, name='send_invoice_email'),
   
    
       # ventes
      
    path('employes/', views.liste_employes, name='liste_employes'),
    path('employes/ajouter/', views.ajouter_employe, name='ajouter_employe'),
    path('employes/modifier/<int:pk>/',
         views.modifier_employe, name='modifier_employe'),
    path('employes/supprimer/<int:pk>/',
         views.supprimer_employe, name='supprimer_employe'),

    # contrat
    path('contrats/', views.liste_contrats, name='liste_contrats'),
    path('contrats/ajouter/', views.ajouter_contrat, name='ajouter_contrat'),
    path('contrats/modifier/<int:pk>/',
         views.modifier_contrat, name='modifier_contrat'),
    path('contrats/supprimer/<int:pk>/',
         views.supprimer_contrat, name='supprimer_contrat'),
    path('progress-liste/', views.liste_progress, name='progress_liste'),
    
    # contrat
  #  path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
     path('utilisateur/ajouter/', views.ajouter_utilisateur, name='ajouter_utilisateur'),
     path('utilisateur/profil/', views.profil_utilisateur, name='profil_utilisateur'),
     path('utilisateur/edit/', views.profile_edit, name='profile_edit'),
     path('report/', views.report_view, name='report'),
     
     path('rapport-livraison/', views.rapport_livraison_view, name='rapport_livraison'),
    

   
   # path('utilisateur/<int:pk>/supprimer/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
     path('', views.login_utilisateur, name='login'),
     path('Logout', views.logout_utilisateur, name='Logout'),
     
  
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)


