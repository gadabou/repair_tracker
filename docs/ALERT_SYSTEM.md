# Système d'Alertes de Dépassement de Délai

## Vue d'ensemble

Ce système envoie automatiquement des emails amicaux aux membres du département où un équipement a pris trop de temps (plus de 14 jours), avec les autres destinataires configurés en copie.

## Fonctionnalités

### 1. Configuration des Destinataires

**URL d'accès** : `/tickets/alerts/config/`

L'interface permet de :
- Sélectionner plusieurs personnes à notifier (avec autocomplétion)
- Configurer deux types de destinataires :
  - **Principal (📧)** : Reçoit tous les emails en copie (CC) quelque soit le département concerné
  - **Département (🎯)** : Reçoit l'email en destinataire direct si son rôle correspond au département où l'équipement est bloqué

- Modifier l'email de notification pour chaque personne
- Voir l'historique des alertes envoyées

#### Types de destinataires expliqués

**Exemple concret** :

Si un téléphone est bloqué 15 jours à l'étape "Logistique" :
- Les membres configurés avec type "Département" ET rôle "Logistique" recevront l'email en **destinataire direct (TO)**
- Tous les membres configurés avec type "Principal" recevront l'email en **copie (CC)**

Cela permet de :
- Cibler directement les responsables concernés
- Garder la direction informée en copie
- Éviter de surcharger les boîtes mail de personnes non concernées

### 2. Détection Automatique

Le système vérifie quotidiennement :
- Tous les tickets actifs (non clôturés, non annulés)
- Le temps passé dans chaque étape
- Déclenchement d'alerte si > 14 jours

### 3. Envoi d'Emails Personnalisés

Les emails sont :
- **Amicaux et professionnels** : Ton cordial, non réprimandant
- **Personnalisés par département** : Salutation adaptée (ex: "Bonjour l'équipe Logistique")
- **Visuellement attractifs** : Design moderne avec code couleur
- **Informatifs** : Toutes les informations du ticket
- **Actionnables** : Liste des actions possibles

#### Contenu de l'email

Chaque email contient :
- Salutation personnalisée selon le département
- Nombre de jours de dépassement (mis en évidence)
- Informations complètes du ticket (équipement, ASC, détenteur, etc.)
- Description du problème initial
- Liste d'actions suggérées :
  - Vérifier l'état de l'équipement
  - Transférer à l'étape suivante si terminé
  - Ajouter un commentaire si difficulté
  - Contacter le support si besoin

### 4. Journal des Alertes

Toutes les alertes sont enregistrées avec :
- Date d'envoi
- Ticket concerné
- Étape et nombre de jours
- Liste des destinataires (TO et CC)
- Statut d'envoi (succès/échec)
- Message d'erreur si applicable

## Utilisation

### Configuration initiale

1. Se connecter en tant qu'administrateur
2. Accéder à `/tickets/alerts/config/`
3. Sélectionner les personnes à notifier :
   - Tapez un nom pour rechercher
   - Sélectionnez plusieurs personnes
4. Pour chaque personne :
   - Vérifier/modifier l'email
   - Choisir le type :
     - **Principal** : Pour la direction, coordinateurs (reçoivent tout en CC)
     - **Département** : Pour les chefs de département (reçoivent selon leur rôle)
5. Enregistrer la configuration

### Exemples de configuration

#### Exemple 1 : Configuration simple
```
- Marie DUPONT (Programme) - Type: Département
- Jean MARTIN (Logistique) - Type: Département
- Sophie BERNARD (Directrice) - Type: Principal
```

**Résultat** : Si un équipement est bloqué en Logistique, Jean reçoit l'email en direct, Sophie en copie.

#### Exemple 2 : Configuration complète
```
- Chef Programme - Type: Département
- Chef Logistique - Type: Département
- Chef E-Santé - Type: Département
- Réparateur principal - Type: Département
- Directeur général - Type: Principal
- Coordinateur projets - Type: Principal
```

### Commande manuelle

Pour tester ou exécuter manuellement :

```bash
# Test sans envoi d'email
python manage.py check_delay_alerts --dry-run

# Envoi réel
python manage.py check_delay_alerts

# Forcer l'envoi même si déjà envoyé dans les 24h
python manage.py check_delay_alerts --force
```

### Configuration automatique (Cron)

Voir le fichier `docs/CRON_SETUP.md` pour les instructions détaillées.

**Recommandation** : Exécuter tous les matins à 9h00 :

```cron
0 9 * * * cd /path/to/kitmanager && python manage.py check_delay_alerts
```

## Configuration Email

### Variables d'environnement

Créer un fichier `.env` :

```env
# Pour la production (Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=mot-de-passe-application-gmail
DEFAULT_FROM_EMAIL=kitmanager@votre-domaine.com

# Pour le développement (console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Configuration Gmail

1. Activer l'authentification à deux facteurs
2. Générer un "Mot de passe d'application"
3. Utiliser ce mot de passe dans `EMAIL_HOST_PASSWORD`

## Logique de Routage des Emails

### Algorithme de sélection des destinataires

```
Pour chaque ticket en dépassement:
  1. Identifier le rôle correspondant à l'étape actuelle
  2. Sélectionner destinataires "Département" ayant ce rôle → TO (destinataires directs)
  3. Sélectionner tous les destinataires "Principal" → CC (copie)
  4. Si aucun destinataire direct trouvé → Envoyer à tous les "Principal" en TO
  5. Générer email personnalisé selon le département
  6. Envoyer et enregistrer dans le journal
```

### Fréquence d'envoi

- **Un email par jour** pour chaque ticket en dépassement
- Envoi quotidien à **7h00 GMT** (via cron)
- L'email est envoyé **chaque jour** jusqu'à ce que l'équipement soit transféré au département suivant
- Une seule alerte par jour par ticket (pas de spam)
- Dès que l'équipement change d'étape, les alertes s'arrêtent pour cette étape
- Si l'équipement reste bloqué dans la nouvelle étape > 14 jours, un nouveau cycle d'alertes commence

**Exemple** :
- Jour 15 en Logistique : Email envoyé à 7h00
- Jour 16 en Logistique : Email envoyé à 7h00
- Jour 17 en Logistique : Email envoyé à 7h00
- Transfert vers Programme : Alertes Logistique arrêtées
- Si bloqué 14 jours en Programme : Nouvelles alertes commencent

## Monitoring

### Vérifier les alertes envoyées

Dans l'interface `/tickets/alerts/config/`, section "Historique des alertes récentes" :
- Date d'envoi
- Ticket concerné
- Étape et durée
- Statut (✅ Envoyé / ❌ Échec)

### Vérifier les logs

```bash
# Logs de la commande cron
tail -f /var/log/kitmanager_alerts.log

# Logs Django
tail -f /path/to/logs/django.log
```

### Base de données

```python
# Voir toutes les alertes
DelayAlertLog.objects.all()

# Alertes récentes
DelayAlertLog.objects.filter(sent_at__gte=timezone.now() - timedelta(days=7))

# Alertes en échec
DelayAlertLog.objects.filter(email_sent_successfully=False)
```

## Dépannage

### Les emails ne partent pas

1. Vérifier la configuration email dans `.env`
2. Tester manuellement :
   ```python
   from django.core.mail import send_mail
   send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```
3. Vérifier les logs d'erreur
4. Vérifier que les destinataires sont actifs

### Aucun destinataire trouvé pour un département

1. Vérifier que des utilisateurs avec le bon rôle sont configurés
2. Vérifier le type de destinataire (Département vs Principal)
3. Ajouter des destinataires Principal comme fallback

### Emails envoyés aux mauvaises personnes

1. Vérifier le type de chaque destinataire
2. Vérifier le rôle des utilisateurs
3. Tester avec `--dry-run` pour voir la répartition

## Modèles de Données

### DelayAlertRecipient

```python
user: ForeignKey(User)              # Utilisateur à notifier
email: EmailField                   # Email (modifiable)
recipient_type: CharField           # PRIMARY ou DEPARTMENT
is_active: BooleanField             # Actif/Inactif
created_at: DateTimeField
updated_at: DateTimeField
```

### DelayAlertLog

```python
ticket: ForeignKey(RepairTicket)
stage: CharField                    # Étape concernée
days_in_stage: IntegerField         # Nombre de jours
recipients: TextField               # Liste TO et CC
sent_at: DateTimeField
email_sent_successfully: BooleanField
error_message: TextField
```

## Améliorations Futures

Possibles évolutions :
- Notifications à J+7 (avertissement) et J+14 (alerte)
- Personnalisation des seuils par département
- Escalade automatique après plusieurs alertes
- Notifications SMS en plus des emails
- Dashboard avec statistiques des délais
- Export des rapports de performance

## Support

Pour toute question ou problème :
1. Consulter les logs
2. Vérifier la configuration
3. Tester avec `--dry-run`
4. Contacter l'administrateur système
