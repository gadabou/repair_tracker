# Guide Rapide - Système d'Alertes

## Mise en route en 5 minutes

### Étape 1 : Configuration des destinataires

1. Connectez-vous en tant qu'administrateur
2. Allez sur : **Tickets → Configuration des alertes** (`/tickets/alerts/config/`)
3. Cliquez dans le champ de recherche et tapez un nom
4. Sélectionnez les personnes à notifier
5. Pour chaque personne sélectionnée :
   - Vérifiez l'email
   - Choisissez le type :
     - **📧 Principal** : Reçoit TOUS les emails en copie (pour direction)
     - **🎯 Département** : Reçoit uniquement les emails de son département (pour chefs d'équipe)
6. Cliquez sur "Enregistrer la configuration"

✅ **Configuration terminée !**

### Étape 2 : Configuration de l'envoi automatique (Production)

#### Option A : Cron simple (recommandé)

```bash
# Ouvrir l'éditeur cron
crontab -e

# Ajouter cette ligne (exécution tous les jours à 7h00 GMT)
0 7 * * * cd /chemin/vers/repair_tracker && python manage.py check_delay_alerts >> /var/log/alerts.log 2>&1

# IMPORTANT: Vérifier que le serveur est en GMT
# timedatectl
# Si nécessaire: sudo timedatectl set-timezone GMT
```

#### Option B : Test manuel

```bash
# Tester sans envoyer d'emails
python manage.py check_delay_alerts --dry-run

# Envoyer réellement les emails
python manage.py check_delay_alerts
```

### Étape 3 : Configuration Email

Créer un fichier `.env` à la racine du projet :

```env
# Pour Gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app
DEFAULT_FROM_EMAIL=repair-tracker@example.com
```

**Note** : Pour Gmail, créez un "Mot de passe d'application" dans les paramètres de sécurité Google.

---

## Comment ça marche ?

### Scénario d'exemple

**Configuration** :
- Marie (Logistique) → Type: Département
- Jean (Programme) → Type: Département
- Sophie (Directrice) → Type: Principal

**Ticket bloqué** : Équipement resté 16 jours en Logistique

**Email envoyé** :
- **À (TO)** : Marie (car elle est Logistique + type Département)
- **CC** : Sophie (car type Principal = toujours en copie)
- **Contenu** : Email amical personnalisé pour l'équipe Logistique

---

## Vérification

### Voir l'historique des alertes

1. Allez sur `/tickets/alerts/config/`
2. Descendez jusqu'à "Historique des alertes récentes"
3. Vous verrez :
   - Date d'envoi
   - Ticket concerné
   - Nombre de jours
   - Statut (✅ ou ❌)

### Vérifier qu'un ticket devrait déclencher une alerte

1. Allez sur le détail d'un ticket
2. Regardez "Temps dans l'étape actuelle"
3. Si > 14 jours ET ticket actif → Une alerte sera envoyée

---

## Questions Fréquentes

### Q: Qui reçoit les emails ?

**R:**
- **Destinataires directs (TO)** : Membres du département concerné (type "Département")
- **En copie (CC)** : Tous les destinataires "Principal"

### Q: À quelle fréquence les emails sont envoyés ?

**R:**
- **Un email par jour** à **7h00 GMT** pour chaque ticket en dépassement
- L'email est envoyé **chaque jour** jusqu'à ce que l'équipement soit transféré au département suivant
- Dès que l'équipement change d'étape, les alertes s'arrêtent automatiquement pour cette étape
- Si l'équipement reste bloqué dans la nouvelle étape > 14 jours, un nouveau cycle d'alertes démarre

**Exemple concret** :
- Jour 15 en Logistique → Email à 7h00
- Jour 16 en Logistique → Email à 7h00
- Jour 17 en Logistique → Email à 7h00
- Équipement transféré → Les alertes Logistique s'arrêtent
- Si bloqué 14+ jours dans la nouvelle étape → Nouvelles alertes

### Q: Comment tester sans envoyer d'emails ?

**R:** Utilisez `python manage.py check_delay_alerts --dry-run`

### Q: Comment changer le seuil de 14 jours ?

**R:** Modifiez la ligne suivante dans `tickets/management/commands/check_delay_alerts.py` :
```python
if days_in_stage >= 14:  # Changez 14 par le nombre souhaité
```

### Q: Les emails partent-ils automatiquement ?

**R:** Oui, si vous avez configuré le cron. Sinon, vous devez lancer manuellement la commande.

---

## Aide-mémoire des commandes

```bash
# Test sans envoi
python manage.py check_delay_alerts --dry-run

# Envoi réel
python manage.py check_delay_alerts

# Forcer l'envoi (ignore la limite 24h)
python manage.py check_delay_alerts --force

# Voir les tâches cron
crontab -l

# Éditer les tâches cron
crontab -e
```

---

## En cas de problème

1. **Aucun email envoyé** :
   - Vérifiez le fichier `.env`
   - Testez : `python manage.py check_delay_alerts --dry-run`
   - Regardez les logs

2. **Mauvais destinataires** :
   - Vérifiez le type de chaque personne (Principal vs Département)
   - Vérifiez le rôle des utilisateurs

3. **Erreur de configuration** :
   - Assurez-vous qu'au moins une personne est configurée
   - Vérifiez que les emails sont valides

---

## Besoin d'aide ?

📚 Documentation complète : `docs/ALERT_SYSTEM.md`
⚙️ Configuration cron : `docs/CRON_SETUP.md`
