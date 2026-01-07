#!/usr/bin/env python
"""
Script pour corriger les comptes superviseurs existants
en activant is_staff=True pour permettre la connexion
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

def fix_supervisor_accounts():
    """Active is_staff pour tous les utilisateurs superviseurs"""

    # Récupérer tous les utilisateurs superviseurs
    supervisors = User.objects.filter(role='SUPERVISOR')

    print(f"Nombre de superviseurs trouvés: {supervisors.count()}")

    updated_count = 0
    for supervisor in supervisors:
        if not supervisor.is_staff:
            supervisor.is_staff = True
            supervisor.save()
            updated_count += 1
            print(f"✓ {supervisor.username} ({supervisor.get_full_name()}) - is_staff activé")
        else:
            print(f"- {supervisor.username} ({supervisor.get_full_name()}) - déjà actif")

    print(f"\n{updated_count} compte(s) superviseur(s) mis à jour.")
    print("Tous les superviseurs peuvent maintenant se connecter à l'application.")

if __name__ == '__main__':
    print("=== Correction des comptes superviseurs ===\n")
    fix_supervisor_accounts()
