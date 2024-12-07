
from django import forms
from .models import Fournisseur, Client, Employe, Contrat,Profile
from django.forms.widgets import DateInput




class ContratForm(forms.ModelForm):
    employe = forms.ModelChoiceField(
        queryset=Employe.objects.filter(actif=False).exclude(contrats__isnull=False),
        label="Sélectionner un Employé",
        empty_label="Choisissez un employé",
    )

    class Meta:
        model = Contrat
        fields = ['employe', 'type_contrat', 'salaire', 'date_debut', 'date_fin']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_contrat'].widget.attrs.update({'class': 'form-control'})
        self.fields['salaire'].widget.attrs.update({'class': 'form-control'})
        self.fields['employe'].widget.attrs.update({'class': 'form-control'})
        self.fields['date_debut'].widget = DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )
        self.fields['date_fin'].widget = DateInput(
            attrs={'class': 'form-control', 'type': 'date'}
        )

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')

        if date_debut and date_fin:
            if date_debut >= date_fin:
                raise forms.ValidationError(
                    "La date de début doit être antérieure à la date de fin."
                )

        return cleaned_data


# forms.py

    




from django import forms
from .models import Categorie

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'description', 'actif']

from django import forms
from .models import Produit

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom', 'description', 'prix', 'categorie', 'actif', 'image']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'categorie': forms.Select(attrs={'class': 'form-control'}),
            'actif': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


# forms.py


class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'email', 'telephone', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={'placeholder': 'Nom du fournisseur', 'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Adresse email', 'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'placeholder': 'Téléphone', 'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'placeholder': 'Adresse', 'rows': 3, 'class': 'form-control'}),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'email', 'telephone',
                  'adresse', 'ville', 'pays', 'code_postal']
        labels = {
            'nom': 'Nom',
            'prenom': 'Prénom',
            'email': 'Adresse Email',
            'telephone': 'Téléphone',
            'adresse': 'Adresse',
            'ville': 'Ville',
            'pays': 'Pays',
            'code_postal': 'Code Postal',
        }
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le nom', }),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le prénom'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'email'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le numéro de téléphone'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Entrez l\'adresse', 'rows': 3}),
            'ville': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez la ville'}),
            'pays': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le pays'}),
            'code_postal': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Entrez le code postal'}),
        }


from django import forms
from .models import Stock


class StockForm(forms.ModelForm):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),  # Enlève le filtre pour récupérer tous les produits
        label="Sélectionner un Produit",
        empty_label="Choisissez un produit",
    )

    class Meta:
        model = Stock
        fields = ['produit', 'quantite', 'statut', 'emplacement']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),  # Champ en lecture seule
            'statut': forms.Select(attrs={'class': 'form-control'}),
            'emplacement': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Définir la valeur par défaut de `quantite` à 0
        self.fields['quantite'].initial = 0
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure les produits ayant déjà un stock associé
        self.fields['produit'].queryset = Produit.objects.filter(stock__isnull=True)

from django import forms
from .models import CommandeApprovisionnement

class CommandeApprovisionnementForm(forms.ModelForm):
    class Meta:
        model = CommandeApprovisionnement
        fields = ['produit', 'fournisseur', 'date_commande', 'quantite', 'commentaire']  # Pas de "status"
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sélectionnez le produit'}),
            'fournisseur': forms.Select(attrs={'class': 'form-control', 'placeholder': 'Sélectionnez le fournisseur'}),
            'date_commande': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantité'}),
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ajoutez un commentaire facultatif'}),
        }





from django import forms
from .models import Livraison, Stock
from django import forms
from .models import Livraison, Stock

class LivraisonForm(forms.ModelForm):
    class Meta:
        model = Livraison
        fields = ['produit', 'prix_unitaire', 'quantite_commande', 'moyen_transport', 'prix_transport', 'date_livraison']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantite_commande': forms.NumberInput(attrs={'class': 'form-control'}),
            'moyen_transport': forms.TextInput(attrs={'class': 'form-control'}),
            'prix_transport': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_livraison': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def save(self, commit=True):
        livraison = super(LivraisonForm, self).save(commit=False)
        # Le fournisseur est récupéré automatiquement via la méthode 'save' du modèle
        if commit:
            livraison.save()
        return livraison
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclure les commandes déjà associées à une livraison
        self.fields['produit'].queryset = CommandeApprovisionnement.objects.filter(livraisons_produit__isnull=True)


from django import forms
from .models import Employe

class EmployeForm(forms.ModelForm):
    class Meta:
        model = Employe
        fields = ['prenom', 'nom', 'email', 'role', 'telephone', 'adresse', 'date_embauche', 'actif']
        widgets = {
            'prenom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le prénom'
            }),
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez l’adresse e-mail'
            }),
            'role': forms.Select(attrs={
                'class': 'form-control'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez le numéro de téléphone'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Entrez l’adresse',
                'rows': 3
            }),
            'date_embauche': forms.DateInput(attrs={
                'class': 'form-control',
                'placeholder': 'YYYY-MM-DD',
                'type': 'date'
            }),
            'actif': forms.Select(attrs={
                'class': 'form-control'
            }),
        }



from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Entrez une adresse email valide.")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d\'utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom d\'utilisateur'}),
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mot de passe'}),
    )

    class Meta:
        model = User
        fields = ['username', 'password']





from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address', 'telephone', 'image']
