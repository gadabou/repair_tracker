# Guide de Démarrage Rapide - Repair Tracker

## Installation en 5 Étapes

### 1. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 2. Appliquer les migrations
```bash
python manage.py migrate
```

### 3. Générer les données de démonstration
```bash
python manage.py seed_demo
```

Cette commande créera :
- 3 régions, 3 districts, 3 communes
- 3 formations sanitaires et 4 zones ASC
- 7 utilisateurs (avec différents rôles)
- 8 ASCs
- 12 équipements
- 7 tickets de réparation avec leurs événements

### 4. Lancer le serveur
```bash
python manage.py runserver
```

### 5. Se connecter
Ouvrez votre navigateur à `http://localhost:8000` et connectez-vous avec :
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

## Comptes de Test Disponibles

| Utilisateur | Mot de passe | Rôle | Description |
|-------------|--------------|------|-------------|
| admin | admin123 | Administrateur | Accès complet |
| superviseur1 | pass123 | Superviseur | Crée tickets, gère ASC |
| programme | pass123 | Programme | Reçoit/envoie tickets |
| logistique | pass123 | Logistique | Route vers réparateurs |
| esante | pass123 | E-Santé | Réparations logicielles |
| reparateur | pass123 | Réparateur | Réparations matérielles |

## Workflow de Test

### Créer un nouveau ticket
1. Se connecter comme `superviseur1` / `pass123`
2. Aller dans "Tickets" → "Nouveau Ticket"
3. Sélectionner un équipement
4. Décrire le problème
5. Choisir le type (matériel/logiciel)
6. Valider

### Gérer le workflow
1. Le superviseur peut envoyer le ticket vers "Programme"
2. Se déconnecter et se reconnecter comme `programme` / `pass123`
3. Confirmer la réception du ticket
4. Envoyer vers "Logistique"
5. Continuer le processus...

## API REST - Exemples

### Lister tous les tickets
```bash
curl http://localhost:8000/api/tickets/ \
  -u admin:admin123
```

### Tickets en retard (> 14 jours)
```bash
curl http://localhost:8000/api/tickets/overdue/ \
  -u admin:admin123
```

### Créer un nouveau ticket via API
```bash
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -u admin:admin123 \
  -d '{
    "equipment": 1,
    "asc": 1,
    "priority": "HIGH",
    "initial_problem_description": "Écran cassé"
  }'
```

### Lister les ASC
```bash
curl http://localhost:8000/api/ascs/ \
  -u admin:admin123
```

### Lister les équipements
```bash
curl http://localhost:8000/api/equipment/ \
  -u admin:admin123
```

## Interface d'Administration

Accédez à l'interface d'admin Django à `http://localhost:8000/admin/` avec :
- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

Vous y trouverez :
- Gestion complète des utilisateurs
- CRUD pour toutes les entités (ASC, Équipements, Tickets, etc.)
- Filtres avancés
- Actions groupées

## Pages Principales de l'Application

- **Dashboard** (`/dashboard/`) : Vue d'ensemble avec statistiques
- **Tickets** (`/tickets/`) : Liste des tickets avec filtres
- **ASCs** (`/accounts/ascs/`) : Liste des agents de santé
- **Équipements** (`/assets/`) : Liste des équipements

## Structure des Délais (Codes Couleur)

Les tickets sont colorés selon leur délai :
- **Vert** : ≤ 7 jours (bon délai)
- **Jaune** : 8-14 jours (attention nécessaire)
- **Rouge** : > 14 jours (action urgente requise)

## Étapes du Workflow

1. **Superviseur** : Point de départ, création du ticket
2. **Programme** : Département programme reçoit et route
3. **Logistique** : Décide de la route (E-Santé ou Réparateur)
4. **E-Santé** : Réparations logicielles
5. **Réparateur** : Réparations matérielles
6. **Retour** : Circuit inverse jusqu'à l'ASC

## Commandes Utiles

```bash
# Créer un superuser supplémentaire
python manage.py createsuperuser

# Réinitialiser les données de démo
python manage.py seed_demo

# Lancer les tests
python manage.py test

# Vérifier le projet
python manage.py check

# Créer des fichiers statiques pour production
python manage.py collectstatic
```

## Dépannage

### Problème : "No module named 'crispy_forms'"
**Solution** : Installer les dépendances
```bash
pip install -r requirements.txt
```

### Problème : "no such table: accounts_user"
**Solution** : Appliquer les migrations
```bash
python manage.py migrate
```

### Problème : Aucun ticket visible
**Solution** : Générer les données de démo
```bash
python manage.py seed_demo
```

## Support

Pour toute question ou problème :
1. Consultez le README.md principal
2. Vérifiez la structure des modèles dans les fichiers `models.py`
3. Consultez l'interface d'admin pour explorer les données

---

**Bon test de l'application Repair Tracker!**
