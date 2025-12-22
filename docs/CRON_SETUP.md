# Configuration de la Tâche Planifiée pour les Alertes de Dépassement de Délai

Ce document explique comment configurer l'envoi automatique des alertes lorsqu'un téléphone dépasse 14 jours dans une étape.

## Commande de vérification

La commande Django suivante vérifie les tickets et envoie les alertes :

```bash
python manage.py check_delay_alerts
```

### Options disponibles

- `--dry-run` : Afficher les alertes sans envoyer d'emails (pour tester)
- `--force` : Forcer l'envoi même si une alerte a déjà été envoyée dans les 24h

### Exemples d'utilisation

```bash
# Test sans envoi d'email
python manage.py check_delay_alerts --dry-run

# Envoi normal
python manage.py check_delay_alerts

# Forcer l'envoi
python manage.py check_delay_alerts --force
```

## Configuration de l'envoi automatique

### Option 1 : Cron (Linux/Mac)

1. Ouvrir l'éditeur crontab :
```bash
crontab -e
```

2. Ajouter la ligne suivante pour exécuter la vérification tous les jours à 7h00 GMT :
```cron
0 9 * * * cd /chemin/vers/repair_tracker && /chemin/vers/python manage.py check_delay_alerts >> /var/log/repair_tracker_alerts.log 2>&1
```

3. Exemples d'horaires :
```cron
# Tous les jours à 7h00 GMT (recommandé - configuration par défaut)
0 7 * * * cd /path/to/project && python manage.py check_delay_alerts

# IMPORTANT: Le fuseau horaire du serveur doit être GMT
# Vérifier avec: timedatectl
# Si besoin: sudo timedatectl set-timezone GMT

# Tous les lundis à 7h00
0 7 * * 1 cd /path/to/project && python manage.py check_delay_alerts

# Deux fois par jour (7h et 14h)
0 7,14 * * * cd /path/to/project && python manage.py check_delay_alerts
```

### Option 2 : Systemd Timer (Linux moderne)

1. Créer le service `/etc/systemd/system/repair-tracker-alerts.service` :
```ini
[Unit]
Description=Repair Tracker - Vérification des alertes de dépassement
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/chemin/vers/repair_tracker
ExecStart=/chemin/vers/python manage.py check_delay_alerts
StandardOutput=journal
StandardError=journal
```

2. Créer le timer `/etc/systemd/system/repair-tracker-alerts.timer` :
```ini
[Unit]
Description=Repair Tracker - Timer pour les alertes quotidiennes
Requires=repair-tracker-alerts.service

[Timer]
OnCalendar=daily
OnCalendar=07:00
Persistent=true
# Note: Temps en GMT

[Install]
WantedBy=timers.target
```

3. Activer et démarrer le timer :
```bash
sudo systemctl daemon-reload
sudo systemctl enable repair-tracker-alerts.timer
sudo systemctl start repair-tracker-alerts.timer

# Vérifier le statut
sudo systemctl status repair-tracker-alerts.timer
sudo systemctl list-timers
```

### Option 3 : Django-crontab (Python)

1. Installer le package :
```bash
pip install django-crontab
```

2. Ajouter à `INSTALLED_APPS` dans `settings.py` :
```python
INSTALLED_APPS = [
    # ...
    'django_crontab',
]
```

3. Ajouter la configuration dans `settings.py` :
```python
CRONJOBS = [
    ('0 9 * * *', 'django.core.management.call_command', ['check_delay_alerts']),
]
```

4. Installer les tâches cron :
```bash
python manage.py crontab add
```

5. Commandes utiles :
```bash
# Voir les tâches
python manage.py crontab show

# Supprimer les tâches
python manage.py crontab remove
```

### Option 4 : Celery (Pour applications avancées)

Si vous utilisez déjà Celery, vous pouvez ajouter une tâche périodique :

1. Dans `tasks.py` :
```python
from celery import shared_task
from django.core.management import call_command

@shared_task
def check_delay_alerts_task():
    call_command('check_delay_alerts')
```

2. Dans `celery.py` :
```python
from celery.schedules import crontab

app.conf.beat_schedule = {
    'check-delay-alerts-daily': {
        'task': 'tickets.tasks.check_delay_alerts_task',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

## Configuration de l'email

### Variables d'environnement

Créer un fichier `.env` à la racine du projet :

```env
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=noreply@repair-tracker.com
```

### Configuration Gmail

1. Activer l'authentification à deux facteurs sur votre compte Gmail
2. Créer un mot de passe d'application :
   - Aller sur https://myaccount.google.com/security
   - Sélectionner "Mots de passe des applications"
   - Créer un nouveau mot de passe pour "Repair Tracker"
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

### Test de configuration email

```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message test', 'from@example.com', ['to@example.com'])
```

## Configuration des destinataires

1. Se connecter à l'application avec un compte administrateur
2. Accéder à `/tickets/alerts/config/`
3. Sélectionner les personnes à notifier
4. Vérifier/modifier leurs emails
5. Enregistrer la configuration

## Monitoring et logs

### Vérifier les logs

```bash
# Logs système (si configuré avec cron)
tail -f /var/log/repair_tracker_alerts.log

# Logs systemd
journalctl -u repair-tracker-alerts.service -f

# Logs Django (si configuré)
tail -f /path/to/django/logs/alerts.log
```

### Vérifier l'historique dans l'application

Les alertes envoyées sont enregistrées dans la table `DelayAlertLog` et visibles dans l'interface de configuration.

## Recommandations

1. **Fréquence** : Exécuter une fois par jour le matin (9h00) est recommandé
2. **Mode test** : Toujours tester avec `--dry-run` avant la mise en production
3. **Monitoring** : Configurer des logs pour surveiller l'exécution
4. **Destinataires** : Vérifier régulièrement que les emails sont à jour
5. **Sécurité** : Ne jamais commiter les identifiants d'email dans Git

## Dépannage

### Les emails ne sont pas envoyés

1. Vérifier la configuration email dans `.env`
2. Tester manuellement : `python manage.py check_delay_alerts --dry-run`
3. Vérifier les logs d'erreur
4. Vérifier que les destinataires sont configurés et actifs

### La tâche cron ne s'exécute pas

1. Vérifier que cron est actif : `sudo systemctl status cron`
2. Vérifier les logs cron : `grep CRON /var/log/syslog`
3. Vérifier les chemins absolus dans la commande cron
4. Tester manuellement la commande

### Aucun dépassement détecté alors qu'il y en a

1. Vérifier le calcul des jours : `ticket.get_time_at_current_stage()`
2. Vérifier le statut des tickets (seuls les tickets actifs sont vérifiés)
3. Vérifier les événements du ticket dans l'interface
