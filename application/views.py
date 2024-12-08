from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Fournisseur, Client, Contrat, Employe,Categorie, Stock, Vente, Client, VenteProduit,Produit
from .forms import FournisseurForm, ClientForm, EmployeForm, ContratForm, ProduitForm,ProfileUpdateForm,UserUpdateForm
from datetime import date
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import logout
from django.db.models import Sum, F, Count
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone

def home(request):
    # Période par défaut : Aujourd'hui
    period = request.GET.get('period', 'day')

    # Exemple de données fictives, remplacez-les par les calculs réels
    if period == 'day':
        categories = ["2018-09-19T00:00:00.000Z", "2018-09-19T01:30:00.000Z", "2018-09-19T02:30:00.000Z"]
        sales = [31, 40, 28]
        revenue = [11, 32, 45]
        customers = [15, 11, 32]
    elif period == 'month':
        categories = ["2018-09-01T00:00:00.000Z", "2018-09-02T00:00:00.000Z", "2018-09-03T00:00:00.000Z"]
        sales = [51, 42, 82]
        revenue = [34, 52, 41]
        customers = [18, 9, 24]
    else:
        categories = ["2018-01-01T00:00:00.000Z", "2018-02-01T00:00:00.000Z", "2018-03-01T00:00:00.000Z"]
        sales = [11, 32, 45]
        revenue = [11, 32, 45]
        customers = [15, 11, 32]

    # Préparer les données pour le graphique
    data_graph = {
        "categories": categories,
        "sales": sales,
        "revenue": revenue,
        "customers": customers,
    }

    # Calcul du nombre total des clients
    total_clients = Client.objects.count()

    # Calcul du nombre total de produits vendus
    total_produits_vendus = VenteProduit.objects.aggregate(
        total=Sum('quantite')
    )['total'] or 0

    # Calcul des produits vendus par catégorie
    categories = Categorie.objects.annotate(
        total_vendus=Sum('produits__venteproduit__quantite')
    ).order_by('-total_vendus')

    # Préparer les données pour le graphique par catégorie
    data_categories = [
        {
            "name": cat.nom,
            "value": cat.total_vendus if cat.total_vendus else 0
        }
        for cat in categories
    ]
    
    # Récupérer les 5 produits les plus vendus
    top_products = Produit.objects.annotate(total_sold=Sum('venteproduit__quantite')) \
        .order_by('-total_sold')[:5]

    # Ajouter les revenus totaux par produit
    for product in top_products:
        total_sold = product.total_sold or 0
        product.total_revenue = total_sold * product.prix

    # Récupérer les 5 dernières ventes
    recent_sales = Vente.objects.order_by('-date')[:5]

    # Récupérer les actions récentes (5 dernières actions)
    recent_actions = LogEntry.objects.select_related('user', 'content_type') \
        .order_by('-action_time')[:5]

    context = {
        'data_graph': data_graph,
        'data_categories': data_categories,
        'total_produits_vendus': total_produits_vendus,
        'total_clients': total_clients,
        'top_products': top_products,  # Les 5 derniers produits
        'recent_actions': recent_actions,
        'recent_sales': recent_sales,
    }

    return render(request, 'index.html', context)


def report_view(request):
    # Obtention de la date actuelle
    today = timezone.now().date()

    # Filtre par défaut : 'today'
    filter_type = request.GET.get('filter', 'today')
    if filter_type == 'today':
        # Filtrer les ventes du jour
        ventes = Vente.objects.filter(date__date=today).annotate(
            total=Sum(F('ventes_produits__quantite') * F('ventes_produits__prix_unitaire'))
        )
    elif filter_type == 'month':
        # Filtrer les ventes du mois en cours
        first_day_of_month = today.replace(day=1)
        ventes = Vente.objects.filter(date__date__gte=first_day_of_month).annotate(
            total=Sum(F('ventes_produits__quantite') * F('ventes_produits__prix_unitaire'))
        )
    elif filter_type == 'year':
        # Filtrer les ventes de l'année en cours
        first_day_of_year = today.replace(month=1, day=1)
        ventes = Vente.objects.filter(date__date__gte=first_day_of_year).annotate(
            total=Sum(F('ventes_produits__quantite') * F('ventes_produits__prix_unitaire'))
        )
    else:
        # Par défaut, on affiche toutes les ventes
        ventes = Vente.objects.all().annotate(
            total=Sum(F('ventes_produits__quantite') * F('ventes_produits__prix_unitaire'))
        )

    # Calcul du revenu total
    total_revenue = ventes.aggregate(Sum('total'))['total__sum'] or 0

    # Calcul du nombre total de clients ayant effectué des ventes
    total_customers = ventes.values('client').distinct().count()

    # Calcul du nombre total de ventes
    total_sales = ventes.count()

    context = {
        'ventes': ventes,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_sales': total_sales,
        'filter_type': filter_type,
    }

    return render(request, 'index.html', context)


def liste_ventes(request):
    # Récupération des ventes et leurs totaux
    ventes = Vente.objects.annotate(total=Sum(F('ventes_produits__quantite') * F('ventes_produits__prix_unitaire')))
    
    # Calcul du total global
    total_global = ventes.aggregate(total_global=Sum('total'))['total_global'] or 0

    return render(request, "ventes/liste_ventes.html", {"ventes": ventes, "total_global": total_global})
from django.shortcuts import render
from .models import Produit

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Vente, Client, Produit, VenteProduit

def ajouter_vente(request):
    if request.method == "POST":
        client_id = request.POST.get("client")
        produits = request.POST.getlist("produit[]")
        quantites = request.POST.getlist("quantite[]")
        prix = request.POST.getlist("prix[]")
        statut_paiement = request.POST.get("statut_paiement", "non_payee")  # Capture du statut de paiement

        if not client_id or not produits:
            messages.error(request, "Veuillez sélectionner un client et au moins un produit.")
            return redirect("ajouter_vente")

        try:
            # Enregistrement de la vente avec le statut de paiement
            client = get_object_or_404(Client, id=client_id)
            nouvelle_vente = Vente.objects.create(client=client, statut_paiement=statut_paiement)

            # Enregistrement des produits et quantités dans la vente
            for produit_id, quantite, prix_unitaire in zip(produits, quantites, prix):
                produit = get_object_or_404(Produit, id=produit_id)
                quantite = int(quantite)
                prix_unitaire = float(prix_unitaire)

                # Enregistrer le produit dans la vente
                VenteProduit.objects.create(
                    vente=nouvelle_vente,
                    produit=produit,
                    quantite=quantite,
                    prix_unitaire=prix_unitaire
                )

            messages.success(request, "La vente a été enregistrée avec succès.")
            return redirect("liste_ventes")

        except Exception as e:
            messages.error(request, f"Une erreur s'est produite : {e}")
            return redirect("ajouter_vente")

    # Récupérer tous les produits sans filtre
    produits = Produit.objects.all()  # Pas de filtre appliqué

    # Récupérer tous les clients
    clients = Client.objects.all()

    return render(request, "ventes/ajouter_vente.html", {"clients": clients, "produits": produits})

def detail_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    produits_vendus = vente.ventes_produits.all()

    # Calcul du total de chaque vente de produit
    for produit_vendu in produits_vendus:
        produit_vendu.total = produit_vendu.quantite * produit_vendu.prix_unitaire

    # Calcul du total global de la vente (sommes des totaux de chaque produit)
    vente_total = produits_vendus.aggregate(
        total=Sum(F('quantite') * F('prix_unitaire'))  # total global
    )['total'] or 0

    return render(request, "ventes/detail_vente.html", {
        "vente": vente,
        "produits_vendus": produits_vendus,
        "vente_total": vente_total,
    })

def modifier_vente(request, pk):
    vente = get_object_or_404(Vente, id=pk)
    clients = Client.objects.all()  # Récupérer tous les clients
    produits = Produit.objects.all()  # Récupérer tous les produits

    if request.method == 'POST':
        # Mettre à jour les informations de la vente
        vente.client = Client.objects.get(id=request.POST['client'])
        
        # Mettre à jour le statut de paiement
        statut_paiement = request.POST.get('statut_paiement')
        if statut_paiement:
            vente.statut_paiement = statut_paiement
        
        vente.save()

        # Supprimer les anciens produits de la vente
        vente.ventes_produits.all().delete()

        # Ajouter les nouveaux produits sélectionnés
        produits_ids = request.POST.getlist('produit[]')
        quantites = request.POST.getlist('quantite[]')
        prix_unitaires = request.POST.getlist('prix[]')

        for produit_id, quantite, prix_unitaire in zip(produits_ids, quantites, prix_unitaires):
            produit = get_object_or_404(Produit, id=produit_id)
            VenteProduit.objects.create(
                vente=vente,
                produit=produit,
                quantite=quantite,
                prix_unitaire=prix_unitaire
            )

        messages.success(request, 'Modification réussie de la vente.')

        return redirect('liste_ventes')

    return render(request, 'ventes/modifier_vente.html', {
        'vente': vente,
        'clients': clients,
        'produits': produits
    })



def supprimer_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)  # Récupère la vente par son ID (pk)

    # Si la requête est de type POST, supprimer la vente
    if request.method == 'POST':
        vente.delete()
        messages.success(request, "La vente a été supprimée avec succès.")
        return redirect('liste_ventes')  # Redirige vers la liste des ventes après suppression

    # Si la méthode n'est pas POST, afficher la page de confirmation
    return render(request, 'supprimer_vente.html', {'vente': vente})



# Create your views here.




from django.shortcuts import render
from .models import Categorie  # Assurez-vous d'importer le modèle Categorie

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Categorie
from .forms import CategorieForm

# Liste des catégories
@login_required
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'categorie/liste_categories.html', {'categories': categories})

# Ajouter une nouvelle catégorie
@login_required
def ajouter_categorie(request):
    if request.method == 'POST':
        form = CategorieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès.")
            return redirect('liste_categories')
    else:
        form = CategorieForm()

    return render(request, 'categorie/ajouter_categorie.html', {'form': form})

# Modifier une catégorie existante
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie
from .forms import CategorieForm
@login_required
def modifier_categorie(request, pk):
    # Récupérer l'objet Categorie correspondant au pk
    categorie = get_object_or_404(Categorie, pk=pk)

    # Si la méthode de la requête est POST, on modifie la catégorie
    if request.method == 'POST':
        form = CategorieForm(request.POST, instance=categorie)
        if form.is_valid():
            form.save()
            return redirect('liste_categories')  # Redirige vers la liste des catégories
    else:
        # Si la méthode est GET, on pré-remplie le formulaire avec les données existantes
        form = CategorieForm(instance=categorie)

    # Retourner le formulaire pour l'affichage dans le template
    return render(request, 'categorie/modifier_categorie.html', {'form': form, 'categorie': categorie})

# Supprimer une catégorie
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie
@login_required
def supprimer_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    
    if request.method == 'POST':
        categorie.delete()
        return redirect('liste_categories')  # Redirige vers la liste des catégories
    
    return render(request, 'categorie/supprimer_categorie.html', {'categorie': categorie})

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .models import Produit

@login_required
def liste_produits(request):
    produits = Produit.objects.all()

    for produit in produits:
        if hasattr(produit, 'stock'):  # Vérifie si le produit a un stock
            total_quantite = produit.stock.quantite
            produit.actif = total_quantite > 0
            if total_quantite < 5:
                messages.warning(request, f"Attention : La quantité de {produit.nom} est inférieure à 5 unités ({total_quantite} unités restantes).")
        else:
            produit.actif = False
            messages.error(request, f"Le produit {produit.nom} n'a pas de stock associé.")

    return render(request, 'produits/liste_produits.html', {'produits': produits})


from django.shortcuts import render, get_object_or_404, redirect
from .models import Produit



from django.shortcuts import render, redirect
from .forms import ProduitForm  # Assurez-vous que votre formulaire est correctement importé

from django.shortcuts import render, redirect
from .forms import ProduitForm

def ajouter_produit(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)  # Inclure request.FILES
        if form.is_valid():
            form.save()
            return redirect('liste_produits')  # Rediriger après enregistrement
    else:
        form = ProduitForm()
    return render(request, 'produits/ajouter_produit.html', {'form': form})

def modifier_produit(request, pk):
    # Récupérer l'objet Produit correspondant au pk
    produit = get_object_or_404(Produit, pk=pk)

    # Si la méthode de la requête est POST, on modifie le produit
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES, instance=produit)  # Inclure request.FILES
        if form.is_valid():
            form.save()
            return redirect('liste_produits')  # Redirige vers la liste des produits
    else:
        # Si la méthode est GET, on pré-remplie le formulaire avec les données existantes
        form = ProduitForm(instance=produit)

    # Retourner le formulaire pour l'affichage dans le template
    return render(request, 'produits/modifier_produit.html', {'form': form, 'produit': produit})

def supprimer_produit(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    
    if request.method == 'POST':
        produit.delete()
        return redirect('liste_produits')  # Redirige vers la liste des produits
    
    return render(request, 'produit/supprimer_produit.html', {'produit': produit})



from django.shortcuts import render, redirect
from .forms import StockForm

def liste_stocks(request):
    stocks = Stock.objects.all().select_related('produit')  # Utilisation de select_related pour optimiser les requêtes
    return render(request, 'stock/liste_stock.html', {'stocks': stocks})
from django.contrib import messages

def ajouter_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            produit = stock.produit

            # Vérifie si un stock existe déjà pour ce produit
            if Stock.objects.filter(produit=produit).exists():
                messages.error(request, "Ce produit est déjà associé à un stock. Vous ne pouvez pas ajouter un nouveau stock pour ce produit.")
                return redirect('liste_stocks')  # Redirige vers la liste des stocks

            # Sinon, enregistrez le stock
            stock.save()
            messages.success(request, "Le stock a été ajouté avec succès.")
            return redirect('liste_stocks')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = StockForm()

    return render(request, 'stock/ajouter_stock.html', {'form': form})


# Vue pour lister les fournisseurs
def modifier_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            return redirect('liste_stocks')  # Rediriger vers la liste des stocks après modification
    else:
        form = StockForm(instance=stock)
    return render(request, 'stock/modifier_stock.html', {'form': form})

def supprimer_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        return redirect('liste_stocks')  # Rediriger vers la liste des stocks après suppression
    return render(request, 'stock/modifier_stock.html', {'stock': stock})



def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'fournisseurs/liste_fournisseurs.html', {'fournisseurs': fournisseurs})

# Vue pour ajouter un fournisseur


def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            product_name = form.cleaned_data.get('nom')
            messages.success(request, f'{product_name} has been added')

            # Redirige vers la liste des fournisseurs
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm()
    return render(request, 'fournisseurs/ajouter_fournisseur.html', {'form': form})

# Vue pour modifier un fournisseur


def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('liste_fournisseurs')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'fournisseurs/modifier_fournisseur.html', {'form': form, 'fournisseur': fournisseur})

# Vue pour supprimer un fournisseur


def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)

    if request.method == 'POST':
        fournisseur.delete()
        return redirect('liste_fournisseurs')

    return render(request, 'supprimer_fournisseur.html', {'fournisseur': fournisseur})


from django.shortcuts import render
from .models import CommandeApprovisionnement

def liste_commandes(request):
    commandes = CommandeApprovisionnement.objects.all()
    return render(request, 'commande/liste_commandes.html', {'commandes': commandes})

from django.shortcuts import render, redirect
from .models import CommandeApprovisionnement
from .forms import CommandeApprovisionnementForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CommandeApprovisionnement, Stock
from .forms import CommandeApprovisionnementForm

def ajouter_commande(request):
    if request.method == 'POST':
        form = CommandeApprovisionnementForm(request.POST)
        if form.is_valid():
            # Enregistrer sans commit pour ajouter le statut si nécessaire
            commande = form.save(commit=False)
            # Forcer le statut "En cours" au cas où cela ne serait pas pris en compte
            commande.status = False  # Utiliser False pour "En cours" (selon votre modèle)
            commande.save()
            return redirect('liste_commandes')  # Rediriger vers la liste des commandes
    else:
        form = CommandeApprovisionnementForm()

    return render(request, 'commande/ajouter_commande.html', {'form': form})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import CommandeApprovisionnement
from .forms import CommandeApprovisionnementForm  # Assurez-vous d'avoir un formulaire pour la commande

def modifier_commande(request, pk):
    commande = get_object_or_404(CommandeApprovisionnement,pk=pk)
    
    if request.method == 'POST':
        form = CommandeApprovisionnementForm(request.POST, instance=commande)
        if form.is_valid():
            form.save()
            messages.success(request, "La commande a été modifiée avec succès.")
            return redirect('liste_commandes')  # Redirige vers la liste des commandes
    else:
        form = CommandeApprovisionnementForm(instance=commande)

    return render(request, 'commande/modifier_commande.html', {'form': form, 'commande': commande})

def supprimer_commande(request, pk):
    commande = get_object_or_404(CommandeApprovisionnement,  pk=pk)

    if request.method == 'POST':
        commande.delete()
        return redirect('liste_commandes')  # Redirige vers la liste des commandes d'approvisionnement

    return render(request, 'supprimer_commande_approvisionnement.html', {'commande': commande})



from django.shortcuts import render, get_object_or_404, redirect
from .models import Livraison
from .forms import LivraisonForm



# Liste des livraisons
def liste_livraisons(request):
    livraisons = Livraison.objects.all()
    return render(request, 'livraisons/liste_livraisons.html', {'livraisons': livraisons})

# Création d'une livraison
from django.shortcuts import render, redirect



from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LivraisonForm
from decimal import Decimal, InvalidOperation

def enregistrer_livraison(request):
    if request.method == 'POST':
        form = LivraisonForm(request.POST)
        if form.is_valid():
            livraison = form.save(commit=False)

            try:
                # Validation des valeurs de type Decimal
                prix_unitaire = livraison.prix_unitaire
                quantite_commande = livraison.quantite_commande
                prix_transport = livraison.prix_transport

                # Vérification que les valeurs sont valides
                if not isinstance(prix_unitaire, Decimal) or not isinstance(prix_transport, Decimal):
                    raise InvalidOperation("Prix unitaire ou prix transport est invalide.")
                if not isinstance(quantite_commande, int) or quantite_commande <= 0:
                    raise ValueError("Quantité commandée doit être un nombre positif.")

                # Calcul des totaux
                livraison.total = prix_unitaire * Decimal(quantite_commande)
                livraison.total_global = livraison.total + prix_transport

                # Sauvegarde de la livraison
                livraison.save()

                messages.success(request, "La livraison a été enregistrée avec succès.")
                return redirect('liste_livraisons')
            except (InvalidOperation, ValueError) as e:
                messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
        else:
            messages.error(request, "Le formulaire contient des erreurs.")

    else:
        form = LivraisonForm()

    return render(request, 'livraisons/livraison_form.html', {'form': form})


    
def details_livraison(request, pk):
    livraison = Livraison.objects.get(pk=pk)
    # Récupérer toutes les livraisons
    livraisons = Livraison.objects.all()
    commande_approvisionnement = livraison.id
    
    return render(request, 'livraisons/details_livraison.html', {'livraison': livraison, 'commande_approvisionnement': commande_approvisionnement, 'livraisons': livraisons})

    
    

# Modification d'une livraison
def modifier_livraison(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)
    if request.method == 'POST':
        form = LivraisonForm(request.POST, instance=livraison)
        if form.is_valid():
            form.save()
            return redirect('liste_livraisons')
    else:
        form = LivraisonForm(instance=livraison)
    return render(request, 'livraisons/livraison_form.html', {'form': form})

# Suppression d'une livraison
def supprimer_livraison(request, pk):
    livraison = get_object_or_404(Livraison, pk=pk)
    if request.method == 'POST':
        livraison.delete()
        return redirect('liste_livraisons')
    return render(request, 'livraisons/delete_livraison.html', {'livraison': livraison})




# Vue pour lister les clients
def liste_clients(request):
    clients = Client.objects.all()
    return render(request, 'clients/liste_clients.html', {'clients': clients})

# Vue pour ajouter un client


def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirige vers la liste des clients
            return redirect('liste_clients')
    else:
        form = ClientForm()
    return render(request, 'clients/ajouter_client.html', {'form': form})

# Vue pour modifier un client


def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            return redirect('liste_clients')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/modifier_client.html', {'form': form, 'client': client})

# Vue pour supprimer un client


def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        return redirect('liste_clients')
    return render(request, 'clients/supprimer_client.html', {'client': client})










# Liste des employés
def liste_employes(request):
    employes = Employe.objects.all()
    return render(request, 'employes/liste_employes.html', {'employes': employes})

# Ajouter un employé


def ajouter_employe(request):
    if request.method == 'POST':
        form = EmployeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_employes')
    else:
        form = EmployeForm()
    return render(request, 'employes/ajouter_employe.html', {'form': form})

# Modifier un employé


def modifier_employe(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        form = EmployeForm(request.POST, instance=employe)
        if form.is_valid():
            form.save()
            return redirect('liste_employes')
    else:
        form = EmployeForm(instance=employe)
    return render(request, 'employes/modifier_employe.html', {'form': form})

# Supprimer un employé


def supprimer_employe(request, pk):
    employe = get_object_or_404(Employe, pk=pk)
    if request.method == 'POST':
        employe.delete()
        return redirect('liste_employes')
    return render(request, 'employes/supprimer_employe.html', {'employe': employe})


def liste_contrats(request):
    contrats = Contrat.objects.all()  # Récupère tous les contrats
    return render(request, 'contrats/liste_contrats.html', {'contrats': contrats})


def ajouter_contrat(request):
    if request.method == 'POST':
        form = ContratForm(request.POST)
        if form.is_valid():
            # Sauvegarde du contrat
            contrat = form.save()

            # Mise à jour du statut de l'employé à "active"
            employe = contrat.employe
            employe.actif = True  # Changer le statut en 'active'
            employe.save()  # Sauvegarder les modifications

            # Redirection après l'ajout réussi
            return redirect('progress_liste')
    else:
        form = ContratForm()  # Formulaire vide pour une requête GET

    return render(request, 'contrats/ajouter_contrat.html', {'form': form})


# Modifier un contrat
def modifier_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        form = ContratForm(request.POST, instance=contrat)
        if form.is_valid():
            form.save()
            # Rediriger vers la liste des contrats
            return redirect('liste_contrats')
    else:
        form = ContratForm(instance=contrat)

    return render(request, 'contrats/modifier_contrat.html', {'form': form})

# Supprimer un contrat


def supprimer_contrat(request, pk):
    contrat = get_object_or_404(Contrat, pk=pk)
    if request.method == 'POST':
        contrat.delete()  # Supprimer uniquement le contrat, l'employé ne sera pas affecté
        # Rediriger vers la liste des contrats
        return redirect('liste_contrats')
    return render(request, 'contrats/supprimer_contrat.html', {'contrat': contrat})


def liste_progress(request):
    contrats = Contrat.objects.all()
    progress_list = []

    for contrat in contrats:
        if contrat.date_debut and contrat.date_fin:
            # Calculer la différence en jours entre la date de fin et la date de début
            total_days = (contrat.date_fin - contrat.date_debut).days

            # Si total_days est supérieur à zéro, calculer la progression
            if total_days > 0:
                elapsed_days = (date.today(
                ) - contrat.date_debut).days if date.today() > contrat.date_debut else 0
                progress = min(max((elapsed_days / total_days) * 100, 0), 100)
            else:
                progress = 100  # Si la date de début et la date de fin sont identiques, on considère que la progression est à 100%

            # Notifications pour les dates de début et de fin du contrat
            if date.today() == contrat.date_debut:
                messages.success(
                    request, f"Le contrat de {contrat.employe.nom} commence aujourd'hui !")

            if date.today() == contrat.date_fin:
                messages.success(
                    request, f"Le contrat de {contrat.employe.nom} arrive à son terme aujourd'hui !")

        else:
            progress = 0  # Si la date de début ou la date de fin est absente, la progression est à 0

        progress_list.append({
            'contrat': contrat,
            'progress': progress
        })

    return render(request, 'contrats/progress_liste.html', {'progress_list': progress_list})




from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CustomUserCreationForm

def ajouter_utilisateur(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Utilisateur créé avec succès !')
            return redirect('home')  # Redirigez vers une page de connexion ou autre
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'utilisateurs/ajouter_utilisateur.html', {'form': form})


from django.contrib.auth import authenticate, login
from .forms import CustomLoginForm

def login_utilisateur(request):
    form = CustomLoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Connexion réussie.')
                return redirect('home')  # Redirige après connexion
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')

    return render(request, 'utilisateurs/login.html', {'form': form})

def logout_utilisateur(request):
    logout(request)  # Déconnexion de l'utilisateur
    messages.success(request, 'Déconnexion réussie.')
    return redirect('login')  
def profil_utilisateur(request): 
    
      return render(request, 'utilisateurs/profile_utilisateur.html', )
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm, UserUpdateForm

@login_required
def profile_edit(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('profil_utilisateur')  # Remplace par le nom de ta vue de profil
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'utilisateurs/profile_utilisateur.html', {'user_form': user_form, 'profile_form': profile_form})



from django.shortcuts import render
from django.db.models import Count, F, Q, ExpressionWrapper, FloatField

def rapport_livraison_view(request):
    fournisseurs = Fournisseur.objects.annotate(
        total_commandes=Count('commandes'),
        commandes_livrees=Count('commandes', filter=Q(commandes__statut='livree')),
        pourcentage_livraison=ExpressionWrapper(
            F('commandes_livrees') * 100.0 / F('total_commandes'),
            output_field=FloatField()
        )
    ).filter(total_commandes__gt=0)

    # Préparer les données pour le chart
    labels = [f.nom for f in fournisseurs]
    series = [f.pourcentage_livraison for f in fournisseurs]

    context = {
        'labels': labels,
        'series': series,
    }
    return render(request, 'rapports/rapport_livraison.html', context)




    
# PDF excel  produits

#############################################################################################


# views.py  e
import openpyxl
from django.http import HttpResponse
from .models import Produit  # Remplacez avec le nom de votre modèle

def exporter_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Produits"

    # En-têtes
    ws.append(['Nom', 'Prix', 'Quantité', 'Emplacement', 'Statut'])

    # Données
    for produit in Produit.objects.all():
        if hasattr(produit, 'stock'):  # Vérifier si le produit a un stock associé
            quantites = f"{produit.stock.quantite} unités"  # Accéder à la quantité du stock associé
            emplacements = produit.stock.emplacement  # Accéder à l'emplacement du stock associé
        else:
            quantites = '0 unités'  # Si le produit n'a pas de stock, définir la quantité à 0
            emplacements = 'Non défini'  # Si le produit n'a pas de stock, l'emplacement est "Non défini"
        
        statut = "Disponible" if produit.actif else "Indisponible"
        ws.append([produit.nom, produit.prix, quantites, emplacements, statut])

    # Création de la réponse HTTP avec le fichier Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="produits.xlsx"'

    # Sauvegarder le fichier Excel dans la réponse
    wb.save(response)
    return response










from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

custom_size = (300, 600)  # Largeur : 300 pts, Hauteur : 600 pts
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from .models import Produit  # Assurez-vous que ce modèle existe
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from .models import Produit

def generer_pdf(request):
    # Lire les paramètres du formulaire
    produits_count = int(request.GET.get("produits_count", 3))  # Nombre de produits par défaut : 3
    exclude_price = request.GET.get("exclude_price") == "on"  # Exclure "Prix" si coché
    only_active = request.GET.get("only_active") == "on"  # Filtrer produits actifs si coché

    # Récupérer les produits depuis la base de données
    produits = Produit.objects.all()
    if only_active:
        produits = produits.filter(actif=True)
    produits = produits[:produits_count]  # Limiter au nombre choisi

    # Construire les données pour le tableau
    en_tetes = ["Nom", "Quantité"]
    if not exclude_price:
        en_tetes.insert(1, "Prix (CFA)")

    tableau_donnees = [en_tetes]  # Ajouter les en-têtes

    for produit in produits:
        if hasattr(produit, 'stock'):  # Vérifier si le produit a un stock
            quantite_totale = produit.stock.quantite  # Accéder à la quantité du stock associé
        else:
            quantite_totale = 0  # Si le produit n'a pas de stock, définir la quantité à 0
        
        ligne = [produit.nom, quantite_totale]
        if not exclude_price:
            ligne.insert(1, f"{produit.prix:,.0f}")
        tableau_donnees.append(ligne)

    # Configurer le PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="produits.pdf"'
    pdf = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Titre
    styles = getSampleStyleSheet()
    titre = Paragraph("Liste Dynamique des Produits", styles["Title"])
    elements.append(titre)

    # Légende
    legende = Paragraph("Ce document est généré selon les paramètres configurés.", styles["BodyText"])
    elements.append(legende)

    # Ajouter un espace
    elements.append(Paragraph("<br/><br/>", styles["BodyText"]))

    # Table
    table = Table(tableau_donnees, colWidths=[150, 100, 120])
    style = TableStyle([  
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ])
    table.setStyle(style)
    elements.append(table)

    # Générer le PDF
    pdf.build(elements)
    return response

# PDF excel  produits

#############################################################################################
