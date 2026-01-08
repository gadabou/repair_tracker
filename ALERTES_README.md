# 📧 Système d'Alertes de Dépassement de Délai

## ✅ Résumé de l'implémentation

Ce document résume le système d'alertes automatiques qui a été mis en place pour notifier les équipes lorsqu'un équipement reste bloqué plus de 14 jours dans un département.

---

## 🎯 Fonctionnalités principales

### 1. **Envoi automatique d'emails quotidiens**
- ⏰ Envoi à **7h00 GMT** chaque jour
- 📅 Répétition **quotidienne** jusqu'au transfert de l'équipement
- 🎯 Emails **personnalisés** selon le département concerné
- 📧 Destinataires **ciblés** avec copie aux responsables

### 2. **Interface de configuration intuitive**
- 🔍 Recherche d'utilisateurs avec **autocomplétion**
- ✅ **Sélection multiple** de destinataires
- ✏️ **Emails modifiables** pour chaque personne
- 🎭 Deux types de destinataires :
  - **Principal** : Reçoit tous les emails en copie (direction)
  - **Département** : Reçoit les emails de son département en direct

### 3. **Emails amicaux et professionnels**
- 💬 Ton cordial et encourageant
- 📊 Design moderne et attractif
- 📋 Informations complètes du ticket
- 💡 Suggestions d'actions concrètes

### 4. **Traçabilité complète**
- 📜 Historique de toutes les alertes envoyées
- ✅ Statut d'envoi (succès/échec)
- 📧 Liste des destinataires (TO et CC)
- ⏱️ Horodatage précis

---

## 📁 Fichiers créés/modifiés

### Modèles de données (`tickets/models.py`)
- ✨ **DelayAlertRecipient** : Configuration des destinataires
- 📝 **DelayAlertLog** : Journal des alertes envoyées

### Vues et URLs (`tickets/views.py`, `tickets/urls.py`)
- 🖥️ `alert_recipients_config` : Interface de configuration
- 🔎 `search_users_api` : API d'autocomplétion
- 🔄 `toggle_recipient_status` : Activer/désactiver un destinataire

### Templates (`templates/tickets/`)
- 🎨 `alert_recipients_config.html` : Page de configuration complète

### Commande de management (`tickets/management/commands/`)
- ⚙️ `check_delay_alerts.py` : Logique de détection et d'envoi

### Configuration (`config/settings.py`)
- 📧 Configuration email (SMTP, Gmail, etc.)

### Migrations
- 🔧 `0003_delayalertlog_delayalertrecipient.py`
- 🔧 `0004_delayalertrecipient_recipient_type.py`

### Documentation
- 📖 **docs/ALERT_SYSTEM.md** : Documentation technique complète
- 🚀 **docs/QUICK_START_ALERTS.md** : Guide de démarrage rapide
- ⚙️ **docs/CRON_SETUP.md** : Configuration détaillée du cron
- 📋 **cron_example.txt** : Exemple de configuration cron prêt à l'emploi
- 📄 **ALERTES_README.md** : Ce fichier

---

## 🚀 Mise en route rapide

### Étape 1 : Accéder à l'interface
```
URL: /tickets/alerts/config/
Accès: Administrateurs uniquement
```

### Étape 2 : Configurer les destinataires
1. Recherchez et sélectionnez les personnes à notifier
2. Pour chaque personne :
   - Vérifiez/modifiez l'email
   - Choisissez le type :
     - **📧 Principal** : Pour la direction (toujours en copie)
     - **🎯 Département** : Pour les chefs d'équipe (selon leur département)
3. Enregistrez

### Étape 3 : Configurer l'envoi automatique
```bash
# Ouvrir l'éditeur cron
crontab -e

# Ajouter la ligne suivante (adapter les chemins)
0 7 * * * cd /chemin/vers/kitmanager && python manage.py check_delay_alerts >> /var/log/alerts.log 2>&1

# Vérifier le fuseau horaire (doit être GMT)
timedatectl
```

### Étape 4 : Configurer l'email (fichier .env)
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=mot-de-passe-application
DEFAULT_FROM_EMAIL=repair-tracker@example.com
```

---

## 💡 Comment ça fonctionne ?

### Scénario d'exemple

**Configuration** :
| Personne | Rôle | Type |
|----------|------|------|
| Marie DUPONT | Logistique | 🎯 Département |
| Jean MARTIN | Programme | 🎯 Département |
| Sophie BERNARD | Directrice | 📧 Principal |

**Ticket bloqué** : Équipement resté 16 jours en Logistique

**Email envoyé** :
- **À (TO)** : marie.dupont@example.com
- **CC** : sophie.bernard@example.com
- **Contenu** : "Bonjour l'équipe Logistique, ..."
- **Envoi** : Chaque jour à 7h00 GMT jusqu'au transfert

**Quand l'équipement est transféré** :
- ✅ Les alertes Logistique s'arrêtent automatiquement
- 🔄 Si bloqué 14+ jours dans la nouvelle étape → Nouvelles alertes démarrent

---

## 📊 Statistiques et suivi

### Interface de monitoring
- Historique des 20 dernières alertes
- Taux de succès/échec
- Tickets concernés avec liens directs

### Commandes de diagnostic
```bash
# Test sans envoi
python manage.py check_delay_alerts --dry-run

# Envoi réel
python manage.py check_delay_alerts

# Forcer l'envoi (ignore la limite quotidienne)
python manage.py check_delay_alerts --force
```

---

## ⚙️ Configuration avancée

### Modifier le seuil de 14 jours
Fichier: `tickets/management/commands/check_delay_alerts.py`
```python
# Ligne ~66
if days_in_stage >= 14:  # Changez 14 par le seuil souhaité
```

### Modifier l'heure d'envoi
```bash
# Changer dans votre crontab
# Exemple pour 8h00 au lieu de 7h00:
0 8 * * * cd /chemin/... && python manage.py check_delay_alerts
```

### Ajouter plusieurs horaires
```bash
# Par exemple à 7h00 et 14h00
0 7,14 * * * cd /chemin/... && python manage.py check_delay_alerts
```

---

## 🔧 Dépannage

### Les emails ne partent pas
1. ✅ Vérifier la configuration dans `.env`
2. ✅ Tester manuellement : `python manage.py check_delay_alerts --dry-run`
3. ✅ Vérifier les logs : `tail -f /var/log/kitmanager_alerts.log`
4. ✅ Tester la connexion email :
   ```python
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
   ```

### La tâche cron ne s'exécute pas
1. ✅ Vérifier que cron est actif : `sudo systemctl status cron`
2. ✅ Vérifier les logs cron : `grep CRON /var/log/syslog`
3. ✅ Vérifier les chemins absolus dans la commande
4. ✅ Tester manuellement la commande complète

### Mauvais destinataires
1. ✅ Vérifier le type de chaque personne (Principal vs Département)
2. ✅ Vérifier le rôle des utilisateurs
3. ✅ Tester avec `--dry-run` pour voir la répartition

---

## 📚 Documentation complète

- 📖 **Documentation technique** : `docs/ALERT_SYSTEM.md`
- 🚀 **Guide de démarrage** : `docs/QUICK_START_ALERTS.md`
- ⚙️ **Configuration cron** : `docs/CRON_SETUP.md`
- 📋 **Exemple cron** : `cron_example.txt`

---

## 🎓 Exemples d'utilisation

### Tester le système sans envoyer d'emails
```bash
python manage.py check_delay_alerts --dry-run
```

**Résultat** :
```
=== Vérification des dépassements de délai ===
Date/Heure: 22/12/2025 07:00
Mode: DRY RUN (aucun email ne sera envoyé)

Destinataires configurés: 3
  - Marie DUPONT (marie@example.com)
  - Jean MARTIN (jean@example.com)
  - Sophie BERNARD (sophie@example.com)

Tickets actifs à vérifier: 15

⚠️  TKT-20251220-ABC123: 16 jours à l'étape "Logistique"
⚠️  TKT-20251218-DEF456: 18 jours à l'étape "Programme"

📧 2 alerte(s) à envoyer

Mode DRY RUN - Aucun email ne sera envoyé
  📧 TKT-20251220-ABC123: 16 jours
  📧 TKT-20251218-DEF456: 18 jours
```

### Voir les destinataires configurés
```python
python manage.py shell
>>> from tickets.models import DelayAlertRecipient
>>> for r in DelayAlertRecipient.objects.filter(is_active=True):
...     print(f"{r.user.get_full_name()} - {r.email} - {r.get_recipient_type_display()}")
```

### Voir l'historique des alertes
```python
>>> from tickets.models import DelayAlertLog
>>> for log in DelayAlertLog.objects.order_by('-sent_at')[:5]:
...     status = "✅" if log.email_sent_successfully else "❌"
...     print(f"{status} {log.ticket.ticket_number} - {log.days_in_stage}j - {log.sent_at}")
```

---

## ✨ Points forts du système

1. **📧 Emails quotidiens** : Rappel constant jusqu'à résolution
2. **🎯 Ciblage intelligent** : Destinataires selon le département concerné
3. **💬 Ton amical** : Encourage l'action sans être réprimandant
4. **📊 Traçabilité** : Historique complet de toutes les alertes
5. **🔧 Flexible** : Configuration facile via interface web
6. **⚡ Automatique** : Aucune intervention manuelle nécessaire
7. **🛡️ Anti-spam** : Une seule alerte par jour maximum
8. **🔄 Auto-arrêt** : S'arrête automatiquement au transfert

---

## 📞 Support

Pour toute question ou assistance :
1. Consultez la documentation dans `docs/`
2. Testez avec `--dry-run`
3. Vérifiez les logs
4. Contactez l'administrateur système

---

**Système développé pour KitManager**
*Amélioration continue du suivi des réparations d'équipements ASC*

---

## 🔐 Sécurité

- ✅ Accès administrateur requis pour la configuration
- ✅ Emails stockés de manière sécurisée
- ✅ Mots de passe email dans fichier `.env` (non commité)
- ✅ Validation des données utilisateur
- ✅ Protection CSRF sur les formulaires

---

**Version** : 1.0
**Date** : Décembre 2025
**Statut** : ✅ Prêt pour la production
