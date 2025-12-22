# Documentation Développeur - Repair Tracker

## Table des matières

1. [Vue d'ensemble du projet](#vue-densemble-du-projet)
2. [Architecture technique](#architecture-technique)
3. [Structure des applications Django](#structure-des-applications-django)
4. [Modèles de données](#modèles-de-données)
5. [Workflow de réparation](#workflow-de-réparation)
6. [API REST](#api-rest)
7. [Interface d'administration](#interface-dadministration)
8. [Vues et Templates](#vues-et-templates)
9. [Configuration et déploiement](#configuration-et-déploiement)
10. [Commandes de gestion](#commandes-de-gestion)
11. [Guide de développement](#guide-de-développement)

---

## Vue d'ensemble du projet

### Description

**Repair Tracker** est un système de gestion et de suivi des réparations d'équipements (téléphones et tablettes) pour les Agents de Santé Communautaire (ASC) au Togo. Le système permet de suivre le cycle complet de réparation, depuis la déclaration d'un problème par un superviseur jusqu'à la réparation et le retour de l'équipement à l'ASC.

### Technologies utilisées

- **Framework**: Django 5.0.14
- **Base de données**: SQLite (développement), PostgreSQL (production)
- **API**: Django REST Framework
- **Frontend**: Bootstrap 5.3, jQuery 3.7.1
- **Déploiement**: Docker, Nginx, Gunicorn
- **Langue**: Français (fr-fr)
- **Fuseau horaire**: Africa/Lome

### Cas d'utilisation principaux

1. **Gestion des ASC**: Enregistrement et suivi des agents de santé communautaire
2. **Gestion des équipements**: Inventaire et assignation des téléphones/tablettes
3. **Tickets de réparation**: Création et suivi des demandes de réparation
4. **Workflow hiérarchique**: Processus de validation à travers différents rôles
5. **Tableau de bord**: Statistiques et indicateurs de performance
6. **API REST**: Intégration avec d'autres systèmes

---

## Architecture technique

### Structure des dossiers

```
repair_tracker/
├── config/                 # Configuration principale du projet
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # Routes URL principales
│   ├── api_urls.py        # Routes API
│   └── wsgi.py            # Configuration WSGI
├── accounts/              # Gestion des utilisateurs et ASC
│   ├── models.py          # User, ASC
│   ├── views.py           # Vues ASC
│   ├── api.py             # API ViewSets
│   ├── forms.py           # Formulaires
│   └── management/        # Commandes de gestion
├── locations/             # Hiérarchie géographique
│   ├── models.py          # Region, District, Commune, etc.
│   └── admin.py           # Interface admin
├── assets/                # Gestion des équipements
│   ├── models.py          # Equipment, EquipmentHistory
│   ├── views.py           # Vues équipements
│   ├── api.py             # API équipements
│   └── forms.py           # Formulaires
├── tickets/               # Système de tickets
│   ├── models.py          # RepairTicket, Issue, Event, Comment
│   ├── views.py           # Vues tickets
│   ├── api.py             # API tickets
│   ├── forms.py           # Formulaires tickets
│   ├── templatetags/      # Tags personnalisés
│   └── management/        # Commandes (rappels)
├── dashboard/             # Tableau de bord
│   └── views.py           # Statistiques et KPIs
├── templates/             # Templates HTML
│   ├── base.html          # Template de base
│   ├── registration/      # Login
│   ├── dashboard/         # Dashboard
│   ├── tickets/           # Templates tickets
│   ├── accounts/          # Templates ASC
│   └── assets/            # Templates équipements
├── static/                # Fichiers statiques
├── media/                 # Fichiers uploadés
│   ├── reception_forms/   # Formulaires de réception
│   └── ticket_attachments/# Pièces jointes tickets
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Configuration Docker
├── docker-compose.yml    # Stack Docker
└── manage.py             # CLI Django
```

### Diagramme d'architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Nginx (Reverse Proxy)                   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Gunicorn + Django Application                   │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐  │
│  │ Accounts │ Locations│  Assets  │ Tickets  │Dashboard │  │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘  │
│                    Django REST Framework                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                  PostgreSQL Database                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Structure des applications Django

Le projet est organisé en **5 applications Django** avec des responsabilités clairement définies :

### 1. **config** - Configuration du projet

**Rôle**: Configuration centrale du projet Django

**Fichiers clés**:
- `settings.py`: Paramètres Django (DB, apps, middleware, etc.)
- `urls.py`: Routage principal
- `api_urls.py`: Routage API REST
- `wsgi.py`: Point d'entrée WSGI

**Caractéristiques importantes**:
```python
# Modèle utilisateur personnalisé
AUTH_USER_MODEL = 'accounts.User'

# Langue et fuseau horaire
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Lome'

# Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    # ...
    'rest_framework',
    'django_filters',
    'crispy_forms',
    'crispy_bootstrap4',
    'accounts',
    'locations',
    'assets',
    'tickets',
    'dashboard',
]
```

---

### 2. **accounts** - Utilisateurs et ASC

**Rôle**: Gestion des utilisateurs avec rôles et des Agents de Santé Communautaire

#### Modèles

**User** (Modèle personnalisé)
```python
class User(AbstractUser):
    """Utilisateur personnalisé avec rôles"""

    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur'),
        ('SUPERVISOR', 'Superviseur'),
        ('PROGRAM', 'Programme'),
        ('LOGISTICS', 'Logistique'),
        ('ESANTE', 'E-santé'),
        ('REPAIRER', 'Réparateur'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True)
```

**ASC** (Agent de Santé Communautaire)
```python
class ASC(models.Model):
    """Agent de Santé Communautaire"""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    supervisor = models.ForeignKey(User, on_delete=models.PROTECT)
    formation_sanitaire = models.ForeignKey('locations.FormationSanitaire')
    zone_asc = models.ForeignKey('locations.ZoneASC')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
```

#### Vues principales

| Vue | URL | Description |
|-----|-----|-------------|
| `asc_list` | `/accounts/ascs/` | Liste des ASC avec recherche |
| `asc_detail` | `/accounts/ascs/<id>/` | Détails d'un ASC |
| `asc_create` | `/accounts/ascs/create/` | Créer un nouvel ASC |

#### API Endpoints

```python
# ASC ViewSet
GET    /api/ascs/              # Liste des ASC
POST   /api/ascs/              # Créer un ASC
GET    /api/ascs/{id}/         # Détails d'un ASC
PUT    /api/ascs/{id}/         # Modifier un ASC
DELETE /api/ascs/{id}/         # Supprimer un ASC

# Filtres disponibles
?search=nom                    # Recherche par nom/prénom/téléphone
```

---

### 3. **locations** - Hiérarchie géographique

**Rôle**: Gestion de la structure géographique du Togo

#### Modèles hiérarchiques

```
Region
  └─> District
       └─> Commune
            └─> FormationSanitaire (Centre de santé)
                 └─> ZoneASC (Zone d'intervention)
```

**Exemple de structure**:
```python
class Region(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

class District(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

class FormationSanitaire(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE)
    type_choices = [('USP', 'USP'), ('CLINIC', 'Clinique'), ...]
    facility_type = models.CharField(max_length=20, choices=type_choices)
```

**Usage**: Ces modèles sont utilisés pour localiser les ASC et générer des rapports géographiques.

---

### 4. **assets** - Gestion des équipements

**Rôle**: Inventaire et suivi des téléphones/tablettes

#### Modèles

**Equipment** (Équipement)
```python
class Equipment(models.Model):
    """Téléphone ou tablette"""

    EQUIPMENT_TYPES = [
        ('PHONE', 'Téléphone'),
        ('TABLET', 'Tablette'),
    ]

    EQUIPMENT_STATUS = [
        ('FUNCTIONAL', 'Fonctionnel'),
        ('FAULTY', 'Défectueux'),
        ('UNDER_REPAIR', 'En réparation'),
        ('RETIRED', 'Retiré'),
    ]

    equipment_type = models.CharField(max_length=10, choices=EQUIPMENT_TYPES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    imei = models.CharField(max_length=50, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=EQUIPMENT_STATUS)
    owner = models.ForeignKey('accounts.ASC', null=True, blank=True)
    assignment_date = models.DateField(null=True, blank=True)
    reception_form = models.FileField(upload_to='reception_forms/', blank=True)
    notes = models.TextField(blank=True)
```

**EquipmentHistory** (Historique)
```python
class EquipmentHistory(models.Model):
    """Piste d'audit pour les changements d'équipement"""

    equipment = models.ForeignKey(Equipment, related_name='history')
    action = models.CharField(max_length=50)  # created, assigned, transferred, retired
    old_owner = models.ForeignKey('accounts.ASC', null=True)
    new_owner = models.ForeignKey('accounts.ASC', null=True)
    changed_by = models.ForeignKey('accounts.User')
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
```

#### Vues principales

| Vue | URL | Description |
|-----|-----|-------------|
| `equipment_list` | `/assets/` | Liste tous les équipements |
| `equipment_detail` | `/assets/<id>/` | Détails + historique |
| `equipment_create` | `/assets/create/` | Créer un équipement |
| `equipment_assign` | `/assets/<id>/assign/` | Assigner à un ASC |
| `asc_assign_equipment` | `/assets/assign-to-asc/<asc_id>/` | Assigner depuis l'ASC |

#### Logique métier importante

**Validation IMEI**: Le numéro IMEI doit être unique
```python
# Dans forms.py
def clean_imei(self):
    imei = self.cleaned_data.get('imei')
    if Equipment.objects.filter(imei=imei).exists():
        raise ValidationError("Un équipement avec cet IMEI existe déjà.")
    return imei
```

**Changement de statut automatique**:
- Quand un ticket est créé → `status = 'UNDER_REPAIR'`
- Quand le ticket est fermé → `status = 'FUNCTIONAL'`

---

### 5. **tickets** - Système de tickets de réparation

**Rôle**: Cœur du système - gestion du workflow de réparation

#### Modèles

**RepairTicket** (Ticket de réparation)
```python
class RepairTicket(models.Model):
    """Ticket de demande de réparation"""

    WORKFLOW_STAGES = [
        ('ASC', 'ASC'),
        ('SUPERVISOR', 'Superviseur'),
        ('PROGRAM', 'Programme'),
        ('LOGISTICS', 'Logistique'),
        ('ESANTE', 'E-santé'),
        ('REPAIRER', 'Réparateur'),
        ('RETURNING_LOGISTICS', 'Retour Logistique'),
        ('RETURNING_PROGRAM', 'Retour Programme'),
        ('RETURNING_SUPERVISOR', 'Retour Superviseur'),
    ]

    TICKET_STATUS = [
        ('OPEN', 'Ouvert'),
        ('IN_PROGRESS', 'En cours'),
        ('REPAIRED', 'Réparé'),
        ('RETURNING', 'En retour'),
        ('CLOSED', 'Fermé'),
        ('CANCELLED', 'Annulé'),
    ]

    PRIORITY_CHOICES = [
        ('LOW', 'Basse'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Haute'),
        ('URGENT', 'Urgente'),
    ]

    ticket_number = models.CharField(max_length=20, unique=True)
    equipment = models.ForeignKey('assets.Equipment', on_delete=models.PROTECT)
    asc = models.ForeignKey('accounts.ASC', on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=TICKET_STATUS)
    current_stage = models.CharField(max_length=30, choices=WORKFLOW_STAGES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    description = models.TextField()
    created_by = models.ForeignKey('accounts.User', related_name='created_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    cancellation_reason = models.TextField(blank=True)
```

**Issue** (Problème déclaré)
```python
class Issue(models.Model):
    """Problème matériel ou logiciel"""

    CATEGORY_CHOICES = [
        ('HARDWARE', 'Matériel'),
        ('SOFTWARE', 'Logiciel'),
        ('OTHER', 'Autre'),
    ]

    ticket = models.ForeignKey(RepairTicket, related_name='issues')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**TicketEvent** (Événement du workflow)
```python
class TicketEvent(models.Model):
    """Suivi détaillé du mouvement du ticket"""

    EVENT_TYPES = [
        ('CREATED', 'Créé'),
        ('RECEIVED', 'Reçu'),
        ('SENT', 'Envoyé'),
        ('REPAIRED', 'Réparé'),
        ('COMMENT', 'Commentaire'),
        ('CANCELLED', 'Annulé'),
    ]

    ticket = models.ForeignKey(RepairTicket, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    stage = models.CharField(max_length=30)
    user = models.ForeignKey('accounts.User')
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='ticket_attachments/', blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
```

**TicketComment** (Commentaire)
```python
class TicketComment(models.Model):
    """Commentaires sur les tickets"""

    ticket = models.ForeignKey(RepairTicket, related_name='comments')
    user = models.ForeignKey('accounts.User')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Vues principales

| Vue | URL | Description |
|-----|-----|-------------|
| `ticket_list` | `/tickets/` | Liste avec filtres (statut, étape) |
| `ticket_detail` | `/tickets/<id>/` | Détails + timeline complète |
| `ticket_create` | `/tickets/create/` | Créer un nouveau ticket |
| `ticket_receive` | `/tickets/<id>/receive/` | Confirmer réception |
| `ticket_send` | `/tickets/<id>/send/` | Envoyer à l'étape suivante |
| `ticket_mark_repaired` | `/tickets/<id>/mark-repaired/` | Marquer comme réparé |
| `ticket_add_comment` | `/tickets/<id>/add-comment/` | Ajouter un commentaire |
| `ticket_cancel` | `/tickets/<id>/cancel/` | Annuler le ticket |

#### API Endpoints

```python
# Tickets ViewSet
GET    /api/tickets/              # Liste des tickets
POST   /api/tickets/              # Créer un ticket
GET    /api/tickets/{id}/         # Détails d'un ticket
PUT    /api/tickets/{id}/         # Modifier un ticket

# Actions personnalisées
GET    /api/tickets/overdue/      # Tickets > 14 jours
GET    /api/tickets/warning/      # Tickets 7-14 jours

# Filtres disponibles
?status=OPEN                       # Par statut
?stage=SUPERVISOR                  # Par étape
?asc_id=5                          # Par ASC
```

---

### 6. **dashboard** - Tableau de bord

**Rôle**: Vue d'ensemble et statistiques du système

#### Vue principale

**dashboard_home** (`/dashboard/`)

Affiche les KPIs suivants:

1. **Statistiques globales**:
   - Nombre total de tickets
   - Tickets ouverts
   - Tickets en cours
   - Tickets fermés

2. **Répartition par statut**:
   - OPEN, IN_PROGRESS, REPAIRED, RETURNING, CLOSED, CANCELLED

3. **Répartition par étape**:
   - Comptage pour chaque étape du workflow

4. **Indicateurs de délai** (code couleur):
   - 🟢 Vert: ≤ 7 jours
   - 🟡 Jaune: 8-14 jours
   - 🔴 Rouge: > 14 jours

5. **Top 5 des blocages**:
   - Identifie les étapes où les tickets sont reçus mais pas envoyés

6. **Durée moyenne de traitement**:
   - Temps moyen entre création et fermeture

**Exemple de calcul de délai**:
```python
def get_delay_days(ticket):
    if ticket.status == 'CLOSED':
        return (ticket.updated_at.date() - ticket.created_at.date()).days
    return (timezone.now().date() - ticket.created_at.date()).days

def get_delay_color(days):
    if days <= 7:
        return 'green'
    elif days <= 14:
        return 'yellow'
    return 'red'
```

---

## Modèles de données

### Relations entre modèles

```
User (1) ──supervises──> (N) ASC
                           │
                           │ owns
                           ▼
FormationSanitaire (1) ──> (N) ASC (1) ──> (N) Equipment
       │                                       │
       │                                       │ has_ticket
       │                                       ▼
ZoneASC (1) ────────────> (N) ASC (1) ──> (N) RepairTicket
                                                │
                                                ├──> (N) Issue
                                                ├──> (N) TicketEvent
                                                └──> (N) TicketComment
```

### Schéma de base de données

#### Table: accounts_user
| Colonne | Type | Description |
|---------|------|-------------|
| id | Integer | Clé primaire |
| username | Varchar(150) | Nom d'utilisateur unique |
| email | Varchar(254) | Email |
| role | Varchar(20) | ADMIN, SUPERVISOR, etc. |
| phone | Varchar(20) | Téléphone |
| is_active | Boolean | Compte actif |

#### Table: accounts_asc
| Colonne | Type | Description |
|---------|------|-------------|
| id | Integer | Clé primaire |
| first_name | Varchar(100) | Prénom |
| last_name | Varchar(100) | Nom |
| phone | Varchar(20) | Téléphone |
| email | Varchar(254) | Email |
| supervisor_id | Foreign Key | Référence User |
| formation_sanitaire_id | Foreign Key | Référence FormationSanitaire |
| zone_asc_id | Foreign Key | Référence ZoneASC |
| is_active | Boolean | ASC actif |

#### Table: assets_equipment
| Colonne | Type | Description |
|---------|------|-------------|
| id | Integer | Clé primaire |
| equipment_type | Varchar(10) | PHONE ou TABLET |
| brand | Varchar(100) | Marque |
| model | Varchar(100) | Modèle |
| imei | Varchar(50) | IMEI (unique) |
| serial_number | Varchar(100) | Numéro de série |
| status | Varchar(20) | FUNCTIONAL, FAULTY, etc. |
| owner_id | Foreign Key | Référence ASC |
| assignment_date | Date | Date d'assignation |
| reception_form | File | Formulaire de réception |

#### Table: tickets_repairticket
| Colonne | Type | Description |
|---------|------|-------------|
| id | Integer | Clé primaire |
| ticket_number | Varchar(20) | Numéro unique (ex: RT-2024-001) |
| equipment_id | Foreign Key | Référence Equipment |
| asc_id | Foreign Key | Référence ASC |
| status | Varchar(20) | OPEN, IN_PROGRESS, etc. |
| current_stage | Varchar(30) | Étape actuelle du workflow |
| priority | Varchar(10) | LOW, MEDIUM, HIGH, URGENT |
| description | Text | Description du problème |
| created_by_id | Foreign Key | Référence User |
| created_at | DateTime | Date de création |
| updated_at | DateTime | Dernière modification |
| cancellation_reason | Text | Raison d'annulation |

#### Table: tickets_ticketevent
| Colonne | Type | Description |
|---------|------|-------------|
| id | Integer | Clé primaire |
| ticket_id | Foreign Key | Référence RepairTicket |
| event_type | Varchar(20) | CREATED, RECEIVED, SENT, etc. |
| stage | Varchar(30) | Étape du workflow |
| user_id | Foreign Key | Utilisateur ayant créé l'événement |
| notes | Text | Notes |
| attachment | File | Pièce jointe |
| timestamp | DateTime | Date/heure de l'événement |

---

## Workflow de réparation

### Flux normal (Aller)

```
1. ASC (Agent) - Problème signalé
         ↓
2. SUPERVISOR - Superviseur reçoit et valide
         ↓
3. PROGRAM - Programme évalue
         ↓
4. LOGISTICS - Logistique coordonne
         ↓
5. ESANTE ou REPAIRER - Réparation effectuée
```

### Flux de retour

```
5. ESANTE/REPAIRER - Marque comme réparé
         ↓
6. RETURNING_LOGISTICS - Retour via logistique
         ↓
7. RETURNING_PROGRAM - Retour via programme
         ↓
8. RETURNING_SUPERVISOR - Retour via superviseur
         ↓
9. ASC - Équipement retourné à l'agent
```

### Statuts et transitions

| Statut | Description | Transitions possibles |
|--------|-------------|----------------------|
| OPEN | Ticket créé | → IN_PROGRESS, CANCELLED |
| IN_PROGRESS | En traitement | → REPAIRED, CANCELLED |
| REPAIRED | Réparation terminée | → RETURNING |
| RETURNING | En cours de retour | → CLOSED |
| CLOSED | Ticket fermé | (terminal) |
| CANCELLED | Ticket annulé | (terminal) |

### Actions disponibles par étape

#### Recevoir un ticket (`ticket_receive`)
```python
# Logique simplifiée
def ticket_receive(request, ticket_id):
    ticket = get_object_or_404(RepairTicket, id=ticket_id)

    # Créer un événement RECEIVED
    TicketEvent.objects.create(
        ticket=ticket,
        event_type='RECEIVED',
        stage=ticket.current_stage,
        user=request.user,
        notes=request.POST.get('notes', '')
    )

    # Mise à jour du statut si nécessaire
    if ticket.status == 'OPEN':
        ticket.status = 'IN_PROGRESS'
        ticket.save()
```

#### Envoyer à l'étape suivante (`ticket_send`)
```python
# Logique simplifiée
def ticket_send(request, ticket_id):
    ticket = get_object_or_404(RepairTicket, id=ticket_id)
    next_stage = request.POST.get('next_stage')

    # Créer un événement SENT
    TicketEvent.objects.create(
        ticket=ticket,
        event_type='SENT',
        stage=next_stage,
        user=request.user,
        notes=request.POST.get('notes', '')
    )

    # Mise à jour de l'étape
    ticket.current_stage = next_stage
    ticket.save()
```

#### Marquer comme réparé (`ticket_mark_repaired`)
```python
# Logique simplifiée
def ticket_mark_repaired(request, ticket_id):
    ticket = get_object_or_404(RepairTicket, id=ticket_id)

    # Créer un événement REPAIRED
    TicketEvent.objects.create(
        ticket=ticket,
        event_type='REPAIRED',
        stage=ticket.current_stage,
        user=request.user,
        notes=request.POST.get('repair_notes', '')
    )

    # Mise à jour du statut et de l'étape
    ticket.status = 'REPAIRED'
    ticket.current_stage = 'RETURNING_LOGISTICS'
    ticket.save()

    # Mise à jour de l'équipement
    ticket.equipment.status = 'FUNCTIONAL'
    ticket.equipment.save()
```

### Validation des transitions

Le système empêche les transitions invalides:
- On ne peut pas sauter d'étapes dans le workflow
- Les actions ne sont disponibles que pour les rôles appropriés
- Un ticket ne peut être modifié une fois fermé ou annulé

---

## API REST

### Configuration

**Framework**: Django REST Framework 3.14+

**Authentication**: Session-based (cookies)

**Permissions**: `IsAuthenticated` (toutes les vues)

**Pagination**: 20 éléments par page

**Filtres**: DjangoFilterBackend

### Endpoints disponibles

#### Tickets API

```http
# Liste des tickets
GET /api/tickets/
Response: {
    "count": 100,
    "next": "http://example.com/api/tickets/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "ticket_number": "RT-2024-001",
            "equipment": 5,
            "equipment_name": "Samsung Galaxy A12",
            "asc": 3,
            "asc_name": "Jean Dupont",
            "status": "IN_PROGRESS",
            "current_stage": "LOGISTICS",
            "priority": "HIGH",
            "description": "Écran cassé",
            "created_at": "2024-12-15T10:30:00Z",
            "updated_at": "2024-12-16T14:20:00Z",
            "delay_days": 7,
            "delay_color": "green"
        }
    ]
}

# Filtres disponibles
GET /api/tickets/?status=OPEN
GET /api/tickets/?stage=SUPERVISOR
GET /api/tickets/?asc_id=3

# Tickets en retard (> 14 jours)
GET /api/tickets/overdue/

# Tickets en avertissement (7-14 jours)
GET /api/tickets/warning/

# Créer un ticket
POST /api/tickets/
Content-Type: application/json
{
    "equipment": 5,
    "asc": 3,
    "priority": "HIGH",
    "description": "Problème de batterie",
    "issues": [
        {
            "category": "HARDWARE",
            "description": "Batterie ne charge plus"
        }
    ]
}
```

#### Équipements API

```http
# Liste des équipements
GET /api/equipment/
Response: {
    "count": 50,
    "results": [
        {
            "id": 1,
            "equipment_type": "PHONE",
            "brand": "Samsung",
            "model": "Galaxy A12",
            "imei": "123456789012345",
            "serial_number": "SN123456",
            "status": "FUNCTIONAL",
            "owner": 3,
            "owner_name": "Jean Dupont",
            "assignment_date": "2024-01-15"
        }
    ]
}

# Filtrer par ASC
GET /api/equipment/?asc_id=3

# Créer un équipement
POST /api/equipment/
Content-Type: application/json
{
    "equipment_type": "PHONE",
    "brand": "Samsung",
    "model": "Galaxy A12",
    "imei": "123456789012345",
    "serial_number": "SN123456",
    "status": "FUNCTIONAL",
    "owner": 3
}
```

#### ASC API

```http
# Liste des ASC
GET /api/ascs/
Response: {
    "count": 30,
    "results": [
        {
            "id": 1,
            "first_name": "Jean",
            "last_name": "Dupont",
            "phone": "+228 90 12 34 56",
            "email": "jean.dupont@example.com",
            "supervisor": 2,
            "supervisor_name": "Marie Martin",
            "formation_sanitaire": 5,
            "formation_sanitaire_name": "USP Lomé Centre",
            "zone_asc": 10,
            "zone_asc_name": "Zone A",
            "is_active": true
        }
    ]
}

# Recherche
GET /api/ascs/?search=Jean

# Créer un ASC
POST /api/ascs/
Content-Type: application/json
{
    "first_name": "Jean",
    "last_name": "Dupont",
    "phone": "+228 90 12 34 56",
    "email": "jean.dupont@example.com",
    "supervisor": 2,
    "formation_sanitaire": 5,
    "zone_asc": 10
}
```

#### Événements API (lecture seule)

```http
# Liste des événements
GET /api/events/
Response: {
    "count": 500,
    "results": [
        {
            "id": 1,
            "ticket": 10,
            "ticket_number": "RT-2024-001",
            "event_type": "RECEIVED",
            "stage": "SUPERVISOR",
            "user": 5,
            "user_name": "Marie Martin",
            "notes": "Équipement bien reçu",
            "timestamp": "2024-12-15T10:30:00Z"
        }
    ]
}

# Filtrer par ticket
GET /api/events/?ticket_id=10
```

### Sérialisation

**Exemple de sérializer avec champs calculés**:
```python
class RepairTicketSerializer(serializers.ModelSerializer):
    equipment_name = serializers.CharField(
        source='equipment.get_full_name',
        read_only=True
    )
    asc_name = serializers.CharField(
        source='asc.get_full_name',
        read_only=True
    )
    delay_days = serializers.SerializerMethodField()
    delay_color = serializers.SerializerMethodField()

    def get_delay_days(self, obj):
        if obj.status == 'CLOSED':
            return (obj.updated_at.date() - obj.created_at.date()).days
        return (timezone.now().date() - obj.created_at.date()).days

    def get_delay_color(self, obj):
        days = self.get_delay_days(obj)
        if days <= 7:
            return 'green'
        elif days <= 14:
            return 'yellow'
        return 'red'
```

---

## Interface d'administration

### Configuration Django Admin

Toutes les applications ont des interfaces admin personnalisées dans leurs fichiers `admin.py` respectifs.

#### Tickets Admin

**Caractéristiques**:
- Inlines pour Issues, Events, Comments
- Filtres: status, priority, current_stage, created_at
- Recherche: ticket_number, equipment__imei, asc__first_name, asc__last_name
- Champs en lecture seule: ticket_number, created_at, updated_at
- Organisation en fieldsets

```python
@admin.register(RepairTicket)
class RepairTicketAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'equipment', 'asc', 'status',
                   'current_stage', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'current_stage', 'created_at']
    search_fields = ['ticket_number', 'equipment__imei',
                    'asc__first_name', 'asc__last_name']
    readonly_fields = ['ticket_number', 'created_at', 'updated_at']

    inlines = [IssueInline, TicketEventInline, TicketCommentInline]

    fieldsets = [
        ('Informations générales', {
            'fields': ['ticket_number', 'equipment', 'asc', 'priority']
        }),
        ('Workflow', {
            'fields': ['status', 'current_stage']
        }),
        ('Description', {
            'fields': ['description']
        }),
        ('Annulation', {
            'fields': ['cancellation_reason'],
            'classes': ['collapse']
        }),
        ('Métadonnées', {
            'fields': ['created_by', 'created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]
```

#### Equipment Admin

```python
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ['equipment_type', 'brand', 'model', 'imei',
                   'status', 'owner', 'assignment_date']
    list_filter = ['equipment_type', 'status', 'brand']
    search_fields = ['imei', 'serial_number', 'brand', 'model']

    inlines = [EquipmentHistoryInline]
```

#### ASC Admin

```python
@admin.register(ASC)
class ASCAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'phone', 'supervisor',
                   'formation_sanitaire', 'is_active']
    list_filter = ['is_active',
                  'formation_sanitaire__commune__district__region',
                  'formation_sanitaire__commune__district',
                  'formation_sanitaire']
    search_fields = ['first_name', 'last_name', 'phone', 'email']

    fieldsets = [
        ('Informations personnelles', {
            'fields': ['first_name', 'last_name', 'phone', 'email']
        }),
        ('Affectation', {
            'fields': ['supervisor', 'formation_sanitaire', 'zone_asc']
        }),
        ('Statut', {
            'fields': ['is_active']
        }),
        ('Notes', {
            'fields': ['notes'],
            'classes': ['collapse']
        }),
    ]
```

### Accès à l'admin

**URL**: `http://localhost:8000/admin/`

**Comptes de test** (après `python manage.py seed_demo`):
- Username: `admin`
- Password: `admin123`

---

## Vues et Templates

### Structure des templates

```
templates/
├── base.html                    # Template de base avec Bootstrap 5
├── registration/
│   └── login.html              # Page de connexion
├── dashboard/
│   └── home.html               # Tableau de bord principal
├── tickets/
│   ├── ticket_list.html        # Liste des tickets
│   ├── ticket_detail.html      # Détails d'un ticket
│   ├── ticket_form.html        # Créer un ticket
│   ├── ticket_receive.html     # Recevoir un ticket
│   ├── ticket_send.html        # Envoyer un ticket
│   ├── ticket_mark_repaired.html # Marquer comme réparé
│   └── ticket_cancel.html      # Annuler un ticket
├── accounts/
│   ├── asc_list.html           # Liste des ASC
│   ├── asc_detail.html         # Détails d'un ASC
│   └── asc_form.html           # Créer un ASC
└── assets/
    ├── equipment_list.html     # Liste des équipements
    ├── equipment_detail.html   # Détails d'un équipement
    ├── equipment_form.html     # Créer un équipement
    └── equipment_assign.html   # Assigner un équipement
```

### Template de base

**base.html** utilise:
- Bootstrap 5.3.0 (CSS + JS)
- Bootstrap Icons 1.11.1
- jQuery 3.7.1
- Navbar responsive avec affichage du rôle
- Système de messages flash Django
- Footer avec copyright

**Exemple de structure**:
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Repair Tracker{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navigation -->
    </nav>

    <main class="container my-4">
        {% if messages %}
            <!-- Messages flash -->
        {% endif %}

        {% block content %}{% endblock %}
    </main>

    <footer class="footer mt-auto py-3 bg-light">
        <!-- Footer -->
    </footer>
</body>
</html>
```

### Vues importantes

#### Liste des tickets avec filtres

```python
def ticket_list(request):
    tickets = RepairTicket.objects.select_related(
        'equipment', 'asc', 'created_by'
    ).order_by('-created_at')

    # Filtres
    status_filter = request.GET.get('status')
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    stage_filter = request.GET.get('stage')
    if stage_filter:
        tickets = tickets.filter(current_stage=stage_filter)

    # Calcul des délais
    for ticket in tickets:
        if ticket.status == 'CLOSED':
            ticket.delay_days = (ticket.updated_at.date() - ticket.created_at.date()).days
        else:
            ticket.delay_days = (timezone.now().date() - ticket.created_at.date()).days

        if ticket.delay_days <= 7:
            ticket.delay_color = 'green'
        elif ticket.delay_days <= 14:
            ticket.delay_color = 'yellow'
        else:
            ticket.delay_color = 'red'

    return render(request, 'tickets/ticket_list.html', {
        'tickets': tickets,
        'status_choices': RepairTicket.TICKET_STATUS,
        'stage_choices': RepairTicket.WORKFLOW_STAGES,
    })
```

#### Détails du ticket avec timeline

```python
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(
        RepairTicket.objects.select_related('equipment', 'asc', 'created_by'),
        id=ticket_id
    )

    # Tous les événements triés chronologiquement
    events = ticket.events.select_related('user').order_by('timestamp')

    # Problèmes déclarés
    issues = ticket.issues.all()

    # Commentaires
    comments = ticket.comments.select_related('user').order_by('created_at')

    return render(request, 'tickets/ticket_detail.html', {
        'ticket': ticket,
        'events': events,
        'issues': issues,
        'comments': comments,
    })
```

### Tags de template personnalisés

**tickets/templatetags/ticket_tags.py**:

```python
from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Permet de chercher dans un dict ou tuple avec une variable"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
```

**Usage**:
```django
{% load ticket_tags %}
{{ STATUS_DICT|lookup:ticket.status }}
```

---

## Configuration et déploiement

### Variables d'environnement

Créer un fichier `.env` à la racine du projet:

```bash
# Django
DEBUG=True
SECRET_KEY=votre-clé-secrète-très-longue-et-aléatoire
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de données (Production)
DATABASE_URL=postgresql://user:password@localhost:5432/repair_tracker

# Email (optionnel)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=votre-email@gmail.com
```

### Installation locale

#### Prérequis
- Python 3.10+
- pip
- virtualenv (recommandé)

#### Étapes

```bash
# 1. Cloner le repository
git clone <url-du-repo>
cd repair_tracker

# 2. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Créer le fichier .env
cp .env.example .env
# Éditer .env avec vos valeurs

# 5. Migrations de la base de données
python manage.py migrate

# 6. Créer un superutilisateur
python manage.py createsuperuser

# 7. (Optionnel) Charger les données de démo
python manage.py seed_demo

# 8. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 9. Lancer le serveur de développement
python manage.py runserver
```

Accéder à l'application: `http://localhost:8000`

### Déploiement Docker

#### Fichiers Docker

**Dockerfile**:
```dockerfile
FROM python:3.13-slim

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code
COPY . .

# Collecte des fichiers statiques
RUN python manage.py collectstatic --noinput

# Script d'entrée
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: repair_tracker
      POSTGRES_USER: repair_user
      POSTGRES_PASSWORD: secure_password
    restart: unless-stopped

  web:
    build: .
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    environment:
      DEBUG: 'False'
      SECRET_KEY: ${SECRET_KEY}
      DATABASE_URL: postgresql://repair_user:secure_password@db:5432/repair_tracker
      ALLOWED_HOSTS: yourdomain.com,www.yourdomain.com
    depends_on:
      - db
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    depends_on:
      - web
    restart: unless-stopped

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

**docker-entrypoint.sh**:
```bash
#!/bin/bash
set -e

# Attendre que PostgreSQL soit prêt
echo "Waiting for PostgreSQL..."
while ! pg_isready -h db -U repair_user; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collecter les fichiers statiques
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Exécuter la commande
exec "$@"
```

#### Commandes Docker

```bash
# Construire et démarrer
docker-compose up -d --build

# Voir les logs
docker-compose logs -f web

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Charger les données de démo
docker-compose exec web python manage.py seed_demo

# Arrêter
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

### Script de déploiement

**deploy.sh**:
```bash
#!/bin/bash
set -e

echo "🚀 Déploiement de Repair Tracker"

# Pull des dernières modifications
echo "📥 Récupération du code..."
git pull

# Build Docker
echo "🔨 Construction des images Docker..."
docker-compose build

# Arrêt des anciens conteneurs
echo "🛑 Arrêt des anciens conteneurs..."
docker-compose down

# Démarrage
echo "▶️  Démarrage des nouveaux conteneurs..."
docker-compose up -d

# Migrations
echo "🔄 Exécution des migrations..."
docker-compose exec -T web python manage.py migrate --noinput

# Collecte des fichiers statiques
echo "📦 Collecte des fichiers statiques..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo "✅ Déploiement terminé!"
echo "🌐 Application disponible sur: http://localhost"
```

### Configuration Nginx

**nginx.conf**:
```nginx
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    upstream django {
        server web:8000;
    }

    server {
        listen 80;
        server_name localhost;

        client_max_body_size 100M;

        location /static/ {
            alias /app/staticfiles/;
            expires 30d;
        }

        location /media/ {
            alias /app/media/;
            expires 7d;
        }

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

---

## Commandes de gestion

### seed_demo

**Chemin**: `accounts/management/commands/seed_demo.py`

**Usage**: Générer un jeu de données de démonstration complet

```bash
python manage.py seed_demo
```

**Ce qui est créé**:

1. **Hiérarchie géographique**:
   - 6 Régions (Lomé, Maritime, Plateaux, Centrale, Kara, Savanes)
   - 39 Districts
   - Communes et Formations Sanitaires
   - Zones ASC

2. **Utilisateurs** (6 rôles):
   - `admin` / `admin123` (ADMIN)
   - `superviseur1` / `pass123` (SUPERVISOR)
   - `programme` / `pass123` (PROGRAM)
   - `logistique` / `pass123` (LOGISTICS)
   - `esante` / `pass123` (ESANTE)
   - `reparateur` / `pass123` (REPAIRER)

3. **8 ASC** avec:
   - Noms aléatoires
   - Téléphones
   - Assignation à différentes Formations Sanitaires
   - Superviseur assigné

4. **Équipements**:
   - 2 téléphones par ASC (16 au total)
   - Marques: Samsung, Tecno, Infinix
   - IMEI générés aléatoirement
   - Statuts variés

5. **15 Tickets de réparation**:
   - Différents statuts et priorités
   - Étapes variées du workflow
   - Problèmes matériels et logiciels
   - Événements de workflow générés

**Code clé**:
```python
class Command(BaseCommand):
    help = 'Génère des données de démonstration'

    def handle(self, *args, **options):
        # Suppression des anciennes données
        self.stdout.write('Suppression des anciennes données...')
        RepairTicket.objects.all().delete()
        Equipment.objects.all().delete()
        ASC.objects.all().delete()
        # ...

        # Création des régions
        regions_data = {
            'Lomé': ['Golfe'],
            'Maritime': ['Vo', 'Yoto', 'Lacs', 'Bas-Mono'],
            # ...
        }

        # Création des utilisateurs
        users = {
            'admin': User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='ADMIN'
            ),
            # ...
        }
```

### send_reminders

**Chemin**: `tickets/management/commands/send_reminders.py`

**Usage**: Envoyer des rappels par email pour les tickets en retard

```bash
python manage.py send_reminders
```

**Logique**:

1. **Tickets à 7 jours** (avertissement):
   - Statut: IN_PROGRESS
   - Délai: exactement 7 jours
   - Sujet: "⚠️ ATTENTION: Ticket en traitement depuis 7 jours"

2. **Tickets à 14 jours** (urgent):
   - Statut: IN_PROGRESS
   - Délai: exactement 14 jours
   - Sujet: "🚨 URGENT: Ticket en traitement depuis 14 jours"

**Contenu de l'email**:
- Numéro du ticket
- Équipement concerné
- ASC concerné
- Étape actuelle
- Nombre de jours écoulés
- Lien direct vers le ticket

**Configuration cron** (recommandé):
```bash
# Exécuter tous les jours à 9h00
0 9 * * * cd /path/to/repair_tracker && /path/to/venv/bin/python manage.py send_reminders
```

**Code clé**:
```python
class Command(BaseCommand):
    help = 'Envoie des rappels pour les tickets en retard'

    def handle(self, *args, **options):
        # Tickets à 7 jours
        seven_days_ago = timezone.now() - timedelta(days=7)
        warning_tickets = RepairTicket.objects.filter(
            status='IN_PROGRESS',
            created_at__date=seven_days_ago.date()
        )

        for ticket in warning_tickets:
            self.send_reminder_email(ticket, urgency='ATTENTION')

        # Tickets à 14 jours
        fourteen_days_ago = timezone.now() - timedelta(days=14)
        urgent_tickets = RepairTicket.objects.filter(
            status='IN_PROGRESS',
            created_at__date=fourteen_days_ago.date()
        )

        for ticket in urgent_tickets:
            self.send_reminder_email(ticket, urgency='URGENT')
```

---

## Guide de développement

### Prérequis

- Python 3.10 ou supérieur
- PostgreSQL 12+ (production)
- Git
- Éditeur de code (VS Code recommandé)

### Configuration de l'environnement de développement

#### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd repair_tracker
```

#### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
```

#### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configuration locale

Créer `.env`:
```bash
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

#### 5. Initialiser la base de données

```bash
python manage.py migrate
python manage.py seed_demo
```

#### 6. Lancer le serveur

```bash
python manage.py runserver
```

### Standards de code

#### Style Python

Suivre **PEP 8**:
```bash
# Installation de flake8
pip install flake8

# Vérification
flake8 .
```

#### Organisation des imports

```python
# 1. Bibliothèque standard
import os
from datetime import datetime

# 2. Bibliothèques tierces
from django.db import models
from rest_framework import serializers

# 3. Imports locaux
from accounts.models import User
from .models import RepairTicket
```

#### Nommage

- **Modèles**: PascalCase (`RepairTicket`, `ASC`)
- **Fonctions/méthodes**: snake_case (`ticket_create`, `get_delay_days`)
- **Constantes**: UPPER_SNAKE_CASE (`TICKET_STATUS`, `WORKFLOW_STAGES`)
- **Variables**: snake_case (`ticket_list`, `asc_name`)

### Structure d'une nouvelle app Django

```bash
# Créer une nouvelle app
python manage.py startapp nouvelle_app

# Structure recommandée
nouvelle_app/
├── __init__.py
├── models.py           # Modèles de données
├── views.py            # Vues (ou views/ pour plusieurs fichiers)
├── api.py              # ViewSets et serializers API
├── forms.py            # Formulaires Django
├── urls.py             # Routes URL
├── admin.py            # Configuration admin
├── apps.py             # Configuration de l'app
├── tests.py            # Tests unitaires
└── management/
    └── commands/       # Commandes de gestion
```

### Ajouter un nouveau modèle

#### 1. Définir le modèle

```python
# models.py
from django.db import models

class NouveauModele(models.Model):
    """Description du modèle"""

    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Nouveau Modèle"
        verbose_name_plural = "Nouveaux Modèles"
        ordering = ['-created_at']

    def __str__(self):
        return self.nom
```

#### 2. Créer les migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 3. Enregistrer dans l'admin

```python
# admin.py
from django.contrib import admin
from .models import NouveauModele

@admin.register(NouveauModele)
class NouveauModeleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'created_at']
    search_fields = ['nom', 'description']
```

### Ajouter une nouvelle vue

#### 1. Créer la vue

```python
# views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import NouveauModele

@login_required
def nouveau_modele_list(request):
    """Liste des nouveaux modèles"""
    objets = NouveauModele.objects.all()

    return render(request, 'nouvelle_app/nouveau_modele_list.html', {
        'objets': objets
    })

@login_required
def nouveau_modele_detail(request, pk):
    """Détails d'un nouveau modèle"""
    objet = get_object_or_404(NouveauModele, pk=pk)

    return render(request, 'nouvelle_app/nouveau_modele_detail.html', {
        'objet': objet
    })
```

#### 2. Configurer les URLs

```python
# urls.py
from django.urls import path
from . import views

app_name = 'nouvelle_app'

urlpatterns = [
    path('', views.nouveau_modele_list, name='list'),
    path('<int:pk>/', views.nouveau_modele_detail, name='detail'),
]
```

#### 3. Inclure dans les URLs principales

```python
# config/urls.py
urlpatterns = [
    # ...
    path('nouvelle-app/', include('nouvelle_app.urls')),
]
```

### Ajouter un endpoint API

#### 1. Créer le serializer

```python
# api.py
from rest_framework import serializers
from .models import NouveauModele

class NouveauModeleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NouveauModele
        fields = '__all__'
```

#### 2. Créer le ViewSet

```python
# api.py (suite)
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

class NouveauModeleViewSet(viewsets.ModelViewSet):
    queryset = NouveauModele.objects.all()
    serializer_class = NouveauModeleSerializer
    permission_classes = [IsAuthenticated]
```

#### 3. Enregistrer dans les URLs API

```python
# config/api_urls.py
from nouvelle_app.api import NouveauModeleViewSet

router.register(r'nouveaux-modeles', NouveauModeleViewSet, basename='nouveau-modele')
```

### Tests

#### Structure des tests

```python
# tests.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import NouveauModele

User = get_user_model()

class NouveauModeleTestCase(TestCase):
    def setUp(self):
        """Configuration avant chaque test"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='ADMIN'
        )
        self.objet = NouveauModele.objects.create(
            nom='Test Objet',
            description='Description de test'
        )

    def test_str_representation(self):
        """Test de la représentation en string"""
        self.assertEqual(str(self.objet), 'Test Objet')

    def test_list_view(self):
        """Test de la vue liste"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/nouvelle-app/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Objet')
```

#### Exécuter les tests

```bash
# Tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test nouvelle_app

# Tests avec coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Génère un rapport HTML
```

### Migrations

#### Créer une migration

```bash
# Migration automatique
python manage.py makemigrations

# Migration avec nom personnalisé
python manage.py makemigrations --name add_new_field_to_model
```

#### Migration de données

```python
# Exemple: migrations/0003_populate_default_values.py
from django.db import migrations

def populate_defaults(apps, schema_editor):
    NouveauModele = apps.get_model('nouvelle_app', 'NouveauModele')
    for obj in NouveauModele.objects.all():
        if not obj.description:
            obj.description = 'Description par défaut'
            obj.save()

class Migration(migrations.Migration):
    dependencies = [
        ('nouvelle_app', '0002_auto_20241215_1200'),
    ]

    operations = [
        migrations.RunPython(populate_defaults),
    ]
```

### Debugging

#### Django Debug Toolbar (recommandé)

```bash
pip install django-debug-toolbar
```

```python
# settings.py
if DEBUG:
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    INTERNAL_IPS = ['127.0.0.1']
```

#### Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

```python
# Utilisation dans le code
import logging
logger = logging.getLogger(__name__)

def ma_fonction():
    logger.debug('Message de debug')
    logger.info('Information')
    logger.warning('Avertissement')
    logger.error('Erreur')
```

### Bonnes pratiques

#### 1. Utiliser select_related et prefetch_related

```python
# ❌ Mauvais (N+1 queries)
tickets = RepairTicket.objects.all()
for ticket in tickets:
    print(ticket.equipment.brand)  # Query pour chaque ticket

# ✅ Bon (1 query)
tickets = RepairTicket.objects.select_related('equipment', 'asc').all()
for ticket in tickets:
    print(ticket.equipment.brand)
```

#### 2. Utiliser get_object_or_404

```python
# ❌ Mauvais
try:
    ticket = RepairTicket.objects.get(id=ticket_id)
except RepairTicket.DoesNotExist:
    # Gérer l'erreur

# ✅ Bon
from django.shortcuts import get_object_or_404
ticket = get_object_or_404(RepairTicket, id=ticket_id)
```

#### 3. Valider les données

```python
# Dans forms.py
class MonFormulaire(forms.ModelForm):
    def clean_imei(self):
        imei = self.cleaned_data.get('imei')
        if len(imei) != 15:
            raise ValidationError("L'IMEI doit contenir 15 caractères")
        return imei
```

#### 4. Utiliser les transactions

```python
from django.db import transaction

@transaction.atomic
def creer_ticket_avec_evenements(data):
    ticket = RepairTicket.objects.create(**data)
    TicketEvent.objects.create(
        ticket=ticket,
        event_type='CREATED',
        stage=ticket.current_stage
    )
    # Si une erreur se produit, tout est annulé
```

#### 5. Sécuriser les vues

```python
from django.contrib.auth.decorators import login_required

@login_required
def ma_vue(request):
    # Seuls les utilisateurs connectés peuvent accéder
    pass
```

### Déploiement en production

#### Checklist de sécurité

- [ ] `DEBUG = False`
- [ ] `SECRET_KEY` généré de manière sécurisée
- [ ] `ALLOWED_HOSTS` configuré correctement
- [ ] HTTPS activé
- [ ] Base de données PostgreSQL
- [ ] Fichiers statiques servis par Nginx
- [ ] `CSRF_COOKIE_SECURE = True`
- [ ] `SESSION_COOKIE_SECURE = True`
- [ ] Sauvegardes automatiques de la base de données

#### Variables d'environnement production

```bash
DEBUG=False
SECRET_KEY=<généré-avec-get_random_secret_key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost:5432/repair_tracker
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=True
```

#### Commandes de déploiement

```bash
# Collecter les fichiers statiques
python manage.py collectstatic --noinput

# Migrations
python manage.py migrate --noinput

# Créer un superutilisateur (si nécessaire)
python manage.py createsuperuser

# Démarrer avec Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## Annexes

### Dépendances complètes

```txt
Django>=5.0,<5.1
djangorestframework>=3.14.0
Pillow>=10.0.0
django-filter>=23.0
django-crispy-forms>=2.0
crispy-bootstrap4>=2.0
python-dateutil>=2.8.2
gunicorn>=21.0.0
psycopg2-binary>=2.9.0
```

### Ressources utiles

- **Documentation Django**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **Bootstrap 5**: https://getbootstrap.com/docs/5.3/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/

### Contributeurs

Pour contribuer au projet:

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### License

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## Support

Pour toute question ou problème:

- Ouvrir une issue sur GitHub
- Contacter l'équipe de développement
- Consulter la documentation Django

---

**Dernière mise à jour**: Décembre 2024
**Version**: 1.0.0
