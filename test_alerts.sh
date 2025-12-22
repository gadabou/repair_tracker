#!/bin/bash

# =============================================================================
# Script de test du système d'alertes de Repair Tracker
# =============================================================================

echo "=================================================="
echo "  Test du Système d'Alertes - Repair Tracker"
echo "=================================================="
echo ""

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Vérifier la configuration Django
echo -e "${YELLOW}1. Vérification de la configuration Django...${NC}"
python manage.py check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Configuration Django OK${NC}"
else
    echo -e "${RED}❌ Erreur de configuration Django${NC}"
    exit 1
fi
echo ""

# 2. Vérifier les migrations
echo -e "${YELLOW}2. Vérification des migrations...${NC}"
python manage.py showmigrations tickets | grep -q "\[X\].*0003_delayalertlog_delayalertrecipient"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration 0003 appliquée${NC}"
else
    echo -e "${RED}❌ Migration 0003 non appliquée${NC}"
    echo "Exécutez: python manage.py migrate"
    exit 1
fi

python manage.py showmigrations tickets | grep -q "\[X\].*0004_delayalertrecipient_recipient_type"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Migration 0004 appliquée${NC}"
else
    echo -e "${RED}❌ Migration 0004 non appliquée${NC}"
    echo "Exécutez: python manage.py migrate"
    exit 1
fi
echo ""

# 3. Vérifier que la commande existe
echo -e "${YELLOW}3. Vérification de la commande check_delay_alerts...${NC}"
python manage.py check_delay_alerts --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Commande check_delay_alerts disponible${NC}"
else
    echo -e "${RED}❌ Commande check_delay_alerts introuvable${NC}"
    exit 1
fi
echo ""

# 4. Test en mode dry-run
echo -e "${YELLOW}4. Test en mode dry-run...${NC}"
echo "---------------------------------------------------"
python manage.py check_delay_alerts --dry-run
echo "---------------------------------------------------"
echo ""

# 5. Vérifier la configuration email
echo -e "${YELLOW}5. Vérification de la configuration email...${NC}"
if [ -f .env ]; then
    if grep -q "EMAIL_HOST=" .env; then
        echo -e "${GREEN}✅ Fichier .env trouvé avec configuration email${NC}"
        echo "Configuration actuelle:"
        grep "EMAIL_" .env | grep -v "PASSWORD" || echo "  (Aucune configuration trouvée)"
    else
        echo -e "${YELLOW}⚠️  Fichier .env trouvé mais sans configuration email${NC}"
        echo "Ajoutez les variables EMAIL_* dans .env"
    fi
else
    echo -e "${YELLOW}⚠️  Fichier .env non trouvé${NC}"
    echo "Créez un fichier .env avec la configuration email"
fi
echo ""

# 6. Vérifier le fuseau horaire du serveur
echo -e "${YELLOW}6. Vérification du fuseau horaire...${NC}"
current_tz=$(timedatectl 2>/dev/null | grep "Time zone" | awk '{print $3}')
if [ -z "$current_tz" ]; then
    echo -e "${YELLOW}⚠️  Impossible de détecter le fuseau horaire${NC}"
elif [ "$current_tz" = "GMT" ] || [ "$current_tz" = "UTC" ]; then
    echo -e "${GREEN}✅ Fuseau horaire: $current_tz (Correct)${NC}"
else
    echo -e "${YELLOW}⚠️  Fuseau horaire actuel: $current_tz${NC}"
    echo "Recommandé: GMT ou UTC"
    echo "Changement: sudo timedatectl set-timezone GMT"
fi
echo ""

# 7. Vérifier les tâches cron
echo -e "${YELLOW}7. Vérification de la tâche cron...${NC}"
crontab -l 2>/dev/null | grep -q "check_delay_alerts"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Tâche cron configurée${NC}"
    echo "Tâche(s) trouvée(s):"
    crontab -l | grep "check_delay_alerts"
else
    echo -e "${YELLOW}⚠️  Aucune tâche cron configurée${NC}"
    echo "Configurez avec: crontab -e"
    echo "Exemple: 0 7 * * * cd $(pwd) && python manage.py check_delay_alerts"
fi
echo ""

# 8. Statistiques de la base de données
echo -e "${YELLOW}8. Statistiques de la base de données...${NC}"
python manage.py shell -c "
from tickets.models import DelayAlertRecipient, DelayAlertLog

recipients = DelayAlertRecipient.objects.count()
active_recipients = DelayAlertRecipient.objects.filter(is_active=True).count()
alerts_sent = DelayAlertLog.objects.count()
successful_alerts = DelayAlertLog.objects.filter(email_sent_successfully=True).count()

print(f'Destinataires configurés: {recipients} (dont {active_recipients} actifs)')
print(f'Alertes envoyées: {alerts_sent} (dont {successful_alerts} avec succès)')
"
echo ""

# 9. Résumé
echo "=================================================="
echo -e "${GREEN}✅ Tests terminés${NC}"
echo "=================================================="
echo ""
echo "Prochaines étapes:"
echo "1. Configurez les destinataires: /tickets/alerts/config/"
echo "2. Ajoutez la tâche cron: crontab -e"
echo "3. Configurez l'email dans .env"
echo "4. Testez l'envoi: python manage.py check_delay_alerts"
echo ""
echo "Documentation:"
echo "- Guide rapide: docs/QUICK_START_ALERTS.md"
echo "- Documentation complète: docs/ALERT_SYSTEM.md"
echo "- Configuration cron: docs/CRON_SETUP.md"
echo ""
