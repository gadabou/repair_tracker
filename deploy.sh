#!/bin/bash

# ============================================================================
# Script de déploiement automatique - Repair Tracker
# ============================================================================
# Ce script déploie automatiquement l'application Repair Tracker avec Docker
# ============================================================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher un message coloré
print_message() {
    echo -e "${2}===> $1${NC}"
}

print_success() {
    print_message "$1" "${GREEN}"
}

print_info() {
    print_message "$1" "${BLUE}"
}

print_warning() {
    print_message "$1" "${YELLOW}"
}

print_error() {
    print_message "$1" "${RED}"
}

# Fonction pour vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé sur ce système!"
        print_info "Veuillez installer Docker: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose n'est pas installé sur ce système!"
        print_info "Veuillez installer Docker Compose: https://docs.docker.com/compose/install/"
        exit 1
    fi

    print_success "Docker et Docker Compose sont installés ✓"
}

# Fonction pour créer le fichier .env s'il n'existe pas
create_env_file() {
    if [ ! -f .env ]; then
        print_warning "Le fichier .env n'existe pas. Création à partir de .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            print_success "Fichier .env créé ✓"
            print_warning "IMPORTANT: Veuillez modifier le fichier .env avec vos configurations!"
            read -p "Appuyez sur Entrée pour continuer après avoir modifié le fichier .env..."
        else
            print_error "Le fichier .env.example n'existe pas!"
            exit 1
        fi
    else
        print_success "Fichier .env existe ✓"
    fi
}

# Fonction pour arrêter et supprimer les anciens conteneurs
cleanup() {
    print_info "Nettoyage des anciens conteneurs..."
    docker-compose down -v 2>/dev/null || docker compose down -v 2>/dev/null || true
    print_success "Nettoyage terminé ✓"
}

# Fonction pour construire les images Docker
build_images() {
    print_info "Construction des images Docker..."
    if docker compose version &> /dev/null; then
        docker compose build --no-cache
    else
        docker-compose build --no-cache
    fi
    print_success "Images Docker construites ✓"
}

# Fonction pour démarrer les conteneurs
start_containers() {
    print_info "Démarrage des conteneurs..."
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    print_success "Conteneurs démarrés ✓"
}

# Fonction pour attendre que la base de données soit prête
wait_for_db() {
    print_info "Attente de la base de données..."
    sleep 10
    print_success "Base de données prête ✓"
}

# Fonction pour afficher les logs
show_logs() {
    print_info "Affichage des logs (Ctrl+C pour quitter)..."
    sleep 2
    if docker compose version &> /dev/null; then
        docker compose logs -f
    else
        docker-compose logs -f
    fi
}

# Fonction pour afficher l'état des conteneurs
show_status() {
    print_info "État des conteneurs:"
    echo ""
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
    echo ""
}

# Fonction pour afficher les informations de connexion
show_connection_info() {
    echo ""
    print_success "╔════════════════════════════════════════════════════════════╗"
    print_success "║         Déploiement terminé avec succès! 🎉               ║"
    print_success "╚════════════════════════════════════════════════════════════╝"
    echo ""
    print_info "📱 Application web:"
    echo "   http://localhost        (via Nginx)"
    echo "   http://localhost:8000   (accès direct Django)"
    echo ""
    print_info "👤 Connexion administrateur:"
    echo "   Utilisateur: admin"
    echo "   Mot de passe: admin123"
    echo ""
    print_info "🗄️  Base de données PostgreSQL:"
    echo "   Host: localhost:5432"
    echo "   Database: repair_tracker"
    echo "   User: admin"
    echo "   Password: repair_password_2024"
    echo ""
    print_info "📋 Commandes utiles:"
    echo "   docker compose logs -f          # Voir les logs"
    echo "   docker compose ps               # État des conteneurs"
    echo "   docker compose stop             # Arrêter les conteneurs"
    echo "   docker compose down             # Arrêter et supprimer"
    echo "   docker compose restart          # Redémarrer"
    echo ""
}

# Menu principal
show_menu() {
    echo ""
    print_info "╔════════════════════════════════════════════════════════════╗"
    print_info "║     Script de Déploiement - Repair Tracker Docker        ║"
    print_info "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Choisissez une option:"
    echo "  1) Déploiement complet (recommandé)"
    echo "  2) Déploiement rapide (sans rebuild)"
    echo "  3) Arrêter les conteneurs"
    echo "  4) Redémarrer les conteneurs"
    echo "  5) Voir les logs"
    echo "  6) Voir l'état des conteneurs"
    echo "  7) Nettoyer et supprimer tout"
    echo "  0) Quitter"
    echo ""
    read -p "Votre choix: " choice
}

# Fonction de déploiement complet
full_deployment() {
    print_info "═══════════════════════════════════════════════════════════"
    print_info "    DÉPLOIEMENT COMPLET DE REPAIR TRACKER"
    print_info "═══════════════════════════════════════════════════════════"
    echo ""

    check_docker
    create_env_file
    cleanup
    build_images
    start_containers
    wait_for_db
    show_status
    show_connection_info

    read -p "Voulez-vous voir les logs en temps réel? (y/n): " view_logs
    if [ "$view_logs" = "y" ] || [ "$view_logs" = "Y" ]; then
        show_logs
    fi
}

# Fonction de déploiement rapide
quick_deployment() {
    print_info "═══════════════════════════════════════════════════════════"
    print_info "    DÉPLOIEMENT RAPIDE (sans rebuild)"
    print_info "═══════════════════════════════════════════════════════════"
    echo ""

    check_docker
    start_containers
    wait_for_db
    show_status
    show_connection_info
}

# Fonction pour arrêter les conteneurs
stop_containers() {
    print_info "Arrêt des conteneurs..."
    if docker compose version &> /dev/null; then
        docker compose stop
    else
        docker-compose stop
    fi
    print_success "Conteneurs arrêtés ✓"
}

# Fonction pour redémarrer les conteneurs
restart_containers() {
    print_info "Redémarrage des conteneurs..."
    if docker compose version &> /dev/null; then
        docker compose restart
    else
        docker-compose restart
    fi
    print_success "Conteneurs redémarrés ✓"
    show_status
}

# Fonction pour nettoyer complètement
full_cleanup() {
    print_warning "ATTENTION: Cette action va supprimer tous les conteneurs et volumes!"
    read -p "Êtes-vous sûr? (y/n): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        print_info "Nettoyage complet..."
        if docker compose version &> /dev/null; then
            docker compose down -v --remove-orphans
        else
            docker-compose down -v --remove-orphans
        fi
        print_success "Nettoyage complet terminé ✓"
    else
        print_info "Opération annulée"
    fi
}

# Boucle principale
main() {
    # Si aucun argument, afficher le menu
    if [ $# -eq 0 ]; then
        while true; do
            show_menu
            case $choice in
                1)
                    full_deployment
                    ;;
                2)
                    quick_deployment
                    ;;
                3)
                    stop_containers
                    ;;
                4)
                    restart_containers
                    ;;
                5)
                    show_logs
                    ;;
                6)
                    show_status
                    ;;
                7)
                    full_cleanup
                    ;;
                0)
                    print_info "Au revoir!"
                    exit 0
                    ;;
                *)
                    print_error "Option invalide!"
                    ;;
            esac
            echo ""
            read -p "Appuyez sur Entrée pour continuer..."
        done
    else
        # Si des arguments sont fournis, exécuter directement
        case $1 in
            deploy|full)
                full_deployment
                ;;
            quick|start)
                quick_deployment
                ;;
            stop)
                stop_containers
                ;;
            restart)
                restart_containers
                ;;
            logs)
                show_logs
                ;;
            status)
                show_status
                ;;
            clean)
                full_cleanup
                ;;
            *)
                print_error "Commande inconnue: $1"
                echo "Usage: $0 [deploy|quick|stop|restart|logs|status|clean]"
                exit 1
                ;;
        esac
    fi
}

# Exécuter le script
main "$@"
