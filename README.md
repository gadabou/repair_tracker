# Repair Tracker - Système de Suivi de Réparations d'Équipements ASC

Application Django complète pour tracer l'acheminement des téléphones/équipements des Agents de Santé Communautaire (ASC) envoyés en réparation.

## Fonctionnalités Principales

### 1. Référentiel ASC
- Gestion complète des ASC avec identité (nom, prénom, code unique, téléphone)
- Localisation hiérarchique (région, district, commune, formation sanitaire, zone ASC)
- Gestion des superviseurs
- CRUD complet avec recherche et filtres

### 2. Gestion des Équipements
- Enregistrement des équipements (téléphone, tablette, autre)
- Informations détaillées : marque, modèle, IMEI/numéro de série
- Suivi de l'état (fonctionnel, en panne, en réparation, réformé)
- Association au propriétaire ASC
- Historique complet des changements

### 3. Workflow de Réparation Traçable
Circuit d'acheminement :
- ASC → Superviseur → Programme → Logistique → (Réparateur OU E-Santé)
- Retour : (Réparateur/E-Santé) → Logistique → Programme → Superviseur → ASC

Fonctionnalités :
- Création de tickets de réparation avec description du problème
- Confirmation de réception à chaque étape
- Confirmation d'envoi vers l'étape suivante
- Timeline complète avec horodatage
- Commentaires et pièces jointes
- Gestion des problèmes (matériel/logiciel)

### 4. Suivi des Délais (Codes Couleur)
- **Vert** : ≤ 7 jours
- **Jaune** : 8-14 jours
- **Rouge** : > 14 jours

### 5. Identification des Blocages
- Affichage de l'étape actuelle
- Identification du détenteur actuel
- Calcul du temps passé à l'étape actuelle
- Top 5 des points de blocage

### 6. Dashboard Complet
Statistiques :
- Total tickets (ouverts, en cours, réparés, clôturés)
- Nombre de tickets rouges et jaunes
- Durée moyenne de traitement
- Top 5 des points de blocage
- Graphiques et tableaux

### 7. Gestion des Rôles et Permissions
Rôles :
- **Administrateur** : Accès complet
- **Superviseur** : Crée tickets, gère ses ASC
- **Programme** : Réception/expédition niveau programme
- **Logistique** : Route vers Réparateur ou E-Santé
- **E-Santé** : Gère réparations logicielles
- **Réparateur** : Gère réparations matérielles

### 8. API REST
API complète avec Django REST Framework :
- Endpoints CRUD pour ASC, Equipment, Tickets, Events
- Filtrage et pagination
- Endpoints spéciaux :
  - `/api/tickets/overdue/` : Tickets en retard (> 14 jours)
  - `/api/tickets/warning/` : Tickets en alerte (7-14 jours)
- Authentication par session

## Installation

### Prérequis
- Python 3.8+
- pip

### Installation et Configuration

```bash
# 1. Cloner ou naviguer vers le projet
cd /path/to/repair_tracker

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Créer les migrations
python manage.py makemigrations
python manage.py migrate

# 4. Générer des données de démonstration
python manage.py seed_demo

# 5. Créer un superuser (optionnel, seed_demo crée déjà admin/admin123)
python manage.py createsuperuser

# 6. Lancer le serveur de développement
python manage.py runserver
```

L'application sera accessible à : `http://localhost:8000`

## Comptes de Test

Les comptes suivants sont créés automatiquement par `seed_demo` :

| Nom d'utilisateur | Mot de passe | Rôle |
|-------------------|--------------|------|
| admin | admin123 | Administrateur |
| superviseur1 | pass123 | Superviseur |
| programme | pass123 | Programme |
| logistique | pass123 | Logistique |
| esante | pass123 | E-Santé |
| reparateur | pass123 | Réparateur |

## Structure du Projet

```
repair_tracker/
├── config/                 # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── api_urls.py        # URLs API
├── accounts/              # Gestion utilisateurs et ASC
│   ├── models.py          # User, ASC
│   ├── views.py
│   ├── api.py
│   └── management/
│       └── commands/
│           └── seed_demo.py
├── locations/             # Localisation géographique
│   └── models.py          # Region, District, Commune, FormationSanitaire, ZoneASC
├── assets/                # Équipements
│   ├── models.py          # Equipment, EquipmentHistory
│   ├── views.py
│   └── api.py
├── tickets/               # Tickets de réparation
│   ├── models.py          # RepairTicket, Issue, TicketEvent, TicketComment
│   ├── views.py
│   └── api.py
├── dashboard/             # Tableau de bord
│   └── views.py
├── templates/             # Templates HTML
│   ├── base.html
│   ├── registration/
│   ├── dashboard/
│   ├── tickets/
│   ├── accounts/
│   └── assets/
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
├── manage.py
├── requirements.txt
└── README.md
```

## Modèles de Données

### Localisation
- **Region** : Régions administratives
- **District** : Districts sanitaires
- **Commune** : Communes
- **FormationSanitaire** : Centres de santé
- **ZoneASC** : Zones d'intervention des ASC

### Comptes
- **User** : Utilisateurs avec rôles (extends AbstractUser)
- **ASC** : Agents de Santé Communautaire

### Équipements
- **Equipment** : Téléphones, tablettes, etc.
- **EquipmentHistory** : Historique des changements

### Tickets
- **RepairTicket** : Ticket principal de réparation
- **Issue** : Problèmes signalés
- **TicketEvent** : Événements du workflow
- **TicketComment** : Commentaires

## API REST

### Endpoints Principaux

```
GET    /api/tickets/                  # Liste des tickets
POST   /api/tickets/                  # Créer un ticket
GET    /api/tickets/{id}/             # Détail d'un ticket
PUT    /api/tickets/{id}/             # Modifier un ticket
DELETE /api/tickets/{id}/             # Supprimer un ticket
GET    /api/tickets/overdue/          # Tickets en retard (> 14j)
GET    /api/tickets/warning/          # Tickets en alerte (7-14j)

GET    /api/equipment/                # Liste des équipements
POST   /api/equipment/                # Créer un équipement
GET    /api/equipment/{id}/           # Détail d'un équipement

GET    /api/ascs/                     # Liste des ASC
POST   /api/ascs/                     # Créer un ASC
GET    /api/ascs/{id}/                # Détail d'un ASC

GET    /api/events/                   # Liste des événements
GET    /api/events/{id}/              # Détail d'un événement
```

### Filtres

```bash
# Filtrer par statut
GET /api/tickets/?status=IN_PROGRESS

# Filtrer par étape
GET /api/tickets/?stage=LOGISTICS

# Combiner les filtres
GET /api/tickets/?status=OPEN&stage=SUPERVISOR
```

### Exemple d'utilisation

```bash
# Récupérer tous les tickets en retard
curl -X GET http://localhost:8000/api/tickets/overdue/ \
  -H "Content-Type: application/json" \
  --user admin:admin123

# Créer un nouveau ticket
curl -X POST http://localhost:8000/api/tickets/ \
  -H "Content-Type: application/json" \
  -d '{"equipment": 1, "asc": 1, "priority": "HIGH", "initial_problem_description": "Écran cassé"}' \
  --user admin:admin123
```

## Interface Web

### Pages Principales

- **`/`** : Redirection vers dashboard ou login
- **`/login/`** : Page de connexion
- **`/dashboard/`** : Tableau de bord avec statistiques
- **`/tickets/`** : Liste des tickets avec filtres
- **`/tickets/{id}/`** : Détail d'un ticket avec timeline
- **`/tickets/create/`** : Créer un nouveau ticket
- **`/accounts/ascs/`** : Liste des ASC
- **`/assets/`** : Liste des équipements
- **`/admin/`** : Interface d'administration Django

## Technologies Utilisées

- **Django 5.0** : Framework web
- **Django REST Framework 3.14+** : API REST
- **Bootstrap 5.3** : Interface UI moderne et responsive
- **Bootstrap Icons** : Icônes
- **SQLite** : Base de données (par défaut)
- **django-crispy-forms** : Formulaires élégants
- **django-filter** : Filtrage avancé

## Déploiement en Production

### Configuration

1. Modifier `settings.py` :
```python
DEBUG = False
ALLOWED_HOSTS = ['votre-domaine.com']
SECRET_KEY = 'votre-clé-secrète-forte'
```

2. Configurer la base de données (PostgreSQL recommandé) :
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'repair_tracker',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

3. Collecter les fichiers statiques :
```bash
python manage.py collectstatic
```

4. Utiliser un serveur WSGI (Gunicorn, uWSGI) avec Nginx

## Support et Contribution

Pour signaler des bugs ou proposer des améliorations, veuillez créer une issue.

## Licence

Projet développé pour le suivi des équipements ASC.

---

**Généré avec Claude Code - Décembre 2025**
