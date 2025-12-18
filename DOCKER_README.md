# 🐳 Déploiement Docker - Repair Tracker

Ce guide explique comment déployer l'application Repair Tracker avec Docker.

## 📋 Prérequis

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- 4 Go de RAM minimum
- 10 Go d'espace disque

## 🚀 Déploiement Automatique (Recommandé)

### Utilisation du script de déploiement

Le script `deploy.sh` automatise entièrement le processus de déploiement.

```bash
# Rendre le script exécutable
chmod +x deploy.sh

# Lancer le menu interactif
./deploy.sh

# Ou directement avec des commandes
./deploy.sh deploy   # Déploiement complet
./deploy.sh quick    # Déploiement rapide
./deploy.sh stop     # Arrêter les conteneurs
./deploy.sh restart  # Redémarrer
./deploy.sh logs     # Voir les logs
./deploy.sh status   # État des conteneurs
./deploy.sh clean    # Nettoyer tout
```

## 🛠️ Déploiement Manuel

### 1. Configuration de l'environnement

Créez un fichier `.env` à partir du template:

```bash
cp .env.example .env
```

Modifiez le fichier `.env` avec vos paramètres:

```env
DEBUG=False
SECRET_KEY=votre-clé-secrète-ultra-sécurisée
ALLOWED_HOSTS=localhost,127.0.0.1,votre-domaine.com

DATABASE_URL=postgresql://repair_user:repair_password_2024@db:5432/repair_tracker

POSTGRES_DB=repair_tracker
POSTGRES_USER=repair_user
POSTGRES_PASSWORD=repair_password_2024
```

### 2. Construction et démarrage

```bash
# Construire les images
docker-compose build

# Démarrer les conteneurs
docker-compose up -d

# Vérifier l'état
docker-compose ps
```

### 3. Initialisation

Les migrations et la création du superutilisateur se font automatiquement au démarrage.

**Identifiants par défaut:**
- Utilisateur: `admin`
- Mot de passe: `admin123`

## 🌐 Accès à l'application

Une fois déployé, l'application est accessible sur:

- **Interface web**: http://localhost (via Nginx)
- **Accès direct Django**: http://localhost:8000
- **Admin Django**: http://localhost/admin

## 📦 Architecture des conteneurs

Le déploiement comprend 3 services:

### 1. **db** (PostgreSQL)
- Image: `postgres:16-alpine`
- Port: `5432`
- Volume: `postgres_data` (persistance des données)

### 2. **web** (Django + Gunicorn)
- Build: Dockerfile custom
- Port: `8000`
- Volumes:
  - Code source (développement)
  - `static_volume` (fichiers statiques)
  - `media_volume` (fichiers uploadés)

### 3. **nginx** (Reverse Proxy)
- Image: `nginx:alpine`
- Port: `80`
- Sert les fichiers statiques et proxie vers Django

## 🔧 Commandes utiles

### Gestion des conteneurs

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f web

# Arrêter les conteneurs
docker-compose stop

# Démarrer les conteneurs
docker-compose start

# Redémarrer
docker-compose restart

# Arrêter et supprimer les conteneurs
docker-compose down

# Arrêter et supprimer tout (y compris les volumes)
docker-compose down -v
```

### Gestion de Django

```bash
# Accéder au shell Django
docker-compose exec web python manage.py shell

# Créer un superutilisateur
docker-compose exec web python manage.py createsuperuser

# Exécuter les migrations
docker-compose exec web python manage.py migrate

# Collecter les fichiers statiques
docker-compose exec web python manage.py collectstatic

# Accéder au shell du conteneur
docker-compose exec web bash
```

### Gestion de la base de données

```bash
# Accéder à PostgreSQL
docker-compose exec db psql -U repair_user -d repair_tracker

# Backup de la base de données
docker-compose exec db pg_dump -U repair_user repair_tracker > backup.sql

# Restaurer la base de données
docker-compose exec -T db psql -U repair_user repair_tracker < backup.sql
```

## 📊 Volumes Docker

Les volumes suivants sont créés pour la persistance des données:

- `postgres_data`: Données PostgreSQL
- `static_volume`: Fichiers statiques Django
- `media_volume`: Fichiers uploadés par les utilisateurs

### Backup des volumes

```bash
# Backup du volume PostgreSQL
docker run --rm -v repair_tracker_postgres_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Backup du volume media
docker run --rm -v repair_tracker_media_volume:/data -v $(pwd):/backup \
  alpine tar czf /backup/media_backup.tar.gz -C /data .
```

## 🔐 Sécurité en Production

### ⚠️ IMPORTANT - Avant de déployer en production:

1. **Changez le SECRET_KEY** dans `.env`
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Désactivez DEBUG**
   ```env
   DEBUG=False
   ```

3. **Configurez ALLOWED_HOSTS**
   ```env
   ALLOWED_HOSTS=votre-domaine.com,www.votre-domaine.com
   ```

4. **Changez les identifiants PostgreSQL**
   ```env
   POSTGRES_PASSWORD=un-mot-de-passe-très-sécurisé
   ```

5. **Activez HTTPS** avec Let's Encrypt (recommandé)

## 🐛 Dépannage

### Le conteneur web ne démarre pas

```bash
# Vérifier les logs
docker-compose logs web

# Reconstruire l'image
docker-compose build --no-cache web
docker-compose up -d web
```

### Erreur de connexion à la base de données

```bash
# Vérifier que PostgreSQL est prêt
docker-compose exec db pg_isready -U repair_user

# Redémarrer la base de données
docker-compose restart db
```

### Les fichiers statiques ne se chargent pas

```bash
# Recollecte les fichiers statiques
docker-compose exec web python manage.py collectstatic --noinput

# Redémarrer nginx
docker-compose restart nginx
```

### Erreur de permissions sur les fichiers

```bash
# Corriger les permissions
docker-compose exec web chown -R root:root /app
```

## 📈 Performance

### Optimisations recommandées

1. **Augmenter le nombre de workers Gunicorn** (dans `docker-compose.yml`):
   ```yaml
   command: gunicorn --bind 0.0.0.0:8000 --workers 4 config.wsgi:application
   ```

2. **Activer la mise en cache** avec Redis:
   ```yaml
   redis:
     image: redis:alpine
     restart: unless-stopped
   ```

3. **Configurer PostgreSQL** pour de meilleures performances

## 🔄 Mise à jour de l'application

```bash
# Arrêter les conteneurs
docker-compose down

# Récupérer les dernières modifications
git pull

# Reconstruire et redémarrer
docker-compose build
docker-compose up -d

# Appliquer les migrations
docker-compose exec web python manage.py migrate
```

## 📞 Support

En cas de problème:

1. Vérifier les logs: `docker-compose logs -f`
2. Vérifier l'état des conteneurs: `docker-compose ps`
3. Consulter la documentation Django
4. Ouvrir une issue sur le repository

## 📄 Licence

Ce projet est sous licence [à définir].

---

**Repair Tracker** - Système de suivi des réparations d'équipements ASC
