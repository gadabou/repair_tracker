# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from accounts.models import User, ASC
from locations.models import Region, District, Site, ZoneASC
from assets.models import Equipment
from tickets.models import RepairTicket, Issue, TicketEvent


class Command(BaseCommand):
    help = 'Génère des données de démonstration pour le système de suivi de réparations'

    def handle(self, *args, **kwargs):
        self.stdout.write('Génération des données de démonstration...')

        # Nettoyer les données existantes (optionnel)
        self.stdout.write('Suppression des anciennes données...')
        RepairTicket.objects.all().delete()
        Equipment.objects.all().delete()
        ASC.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        ZoneASC.objects.all().delete()
        Site.objects.all().delete()
        District.objects.all().delete()
        Region.objects.all().delete()

        # Créer les régions
        self.stdout.write('Création des régions...')
        atacora = Region.objects.create(name='Atacora', code='ATQ')
        atlantique = Region.objects.create(name='Atlantique', code='ATL')
        borgou = Region.objects.create(name='Borgou', code='BRG')

        # Créer les districts
        self.stdout.write('Création des districts...')
        natitingou = District.objects.create(region=atacora, name='Natitingou', code='NAT')
        ouidah = District.objects.create(region=atlantique, name='Ouidah', code='OUI')
        parakou = District.objects.create(region=borgou, name='Parakou', code='PAR')

        # Créer les sites
        self.stdout.write('Création des sites...')
        site1 = Site.objects.create(
            district=natitingou,
            name='CS Tanguiéta Centre',
            code='TGT-CS-01',
            phone='97123456',
            address='Route Nationale 1'
        )
        site2 = Site.objects.create(
            district=ouidah,
            name='CS Ouidah Zone 1',
            code='OUI-CS-01',
            phone='97234567'
        )
        site3 = Site.objects.create(
            district=parakou,
            name='CS Parakou Centre',
            code='PAR-CS-01',
            phone='97345678'
        )

        # Créer les zones ASC
        self.stdout.write('Création des zones ASC...')
        zones = [
            ZoneASC.objects.create(site=site1, name='Zone A', code='ZA'),
            ZoneASC.objects.create(site=site1, name='Zone B', code='ZB'),
            ZoneASC.objects.create(site=site2, name='Zone 1', code='Z1'),
            ZoneASC.objects.create(site=site3, name='Zone Centre', code='ZC'),
        ]

        # Créer les utilisateurs avec différents rôles
        self.stdout.write('Création des utilisateurs...')

        # Admin (si n'existe pas déjà)
        admin, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@kitmanager.local',
                'role': 'ADMIN',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Superuser créé: admin / admin123'))

        # Superviseurs
        superviseur1 = User.objects.create_user(
            username='superviseur1',
            password='pass123',
            first_name='Jean',
            last_name='Dossou',
            email='superviseur1@example.com',
            role='SUPERVISOR',
            phone='97111111',
            site=site1
        )

        superviseur2 = User.objects.create_user(
            username='superviseur2',
            password='pass123',
            first_name='Marie',
            last_name='Adjovi',
            email='superviseur2@example.com',
            role='SUPERVISOR',
            phone='97222222',
            site=site2
        )

        # Programme
        programme = User.objects.create_user(
            username='programme',
            password='pass123',
            first_name='Paul',
            last_name='Kossou',
            email='programme@example.com',
            role='PROGRAM',
            phone='97333333'
        )

        # Logistique
        logistique = User.objects.create_user(
            username='logistique',
            password='pass123',
            first_name='Sophie',
            last_name='Gbèdo',
            email='logistique@example.com',
            role='LOGISTICS',
            phone='97444444'
        )

        # E-Santé
        esante = User.objects.create_user(
            username='esante',
            password='pass123',
            first_name='David',
            last_name='Azonhiho',
            email='esante@example.com',
            role='ESANTE',
            phone='97555555'
        )

        # Réparateur
        reparateur = User.objects.create_user(
            username='reparateur',
            password='pass123',
            first_name='Jacques',
            last_name='Aho',
            email='reparateur@example.com',
            role='REPAIRER',
            phone='97666666'
        )

        # Créer les ASCs
        self.stdout.write('Création des ASCs...')
        ascs = []
        asc_names = [
            ('Aïcha', 'Sanni', 'F'),
            ('Ramatou', 'Boukari', 'F'),
            ('Moussa', 'Tamou', 'M'),
            ('Célestine', 'Codjo', 'F'),
            ('Hervé', 'Agossou', 'M'),
            ('Fatima', 'Issiaka', 'F'),
            ('René', 'Hounkpè', 'M'),
            ('Estelle', 'Gbèmisola', 'F'),
        ]

        sites = [site1, site1, site2, site2, site3, site3, site1, site2]
        superviseurs = [superviseur1, superviseur1, superviseur2, superviseur2, superviseur1, superviseur1, superviseur1, superviseur2]

        for i, ((first_name, last_name, gender), site, sup) in enumerate(zip(asc_names, sites, superviseurs)):
            asc = ASC.objects.create(
                first_name=first_name,
                last_name=last_name,
                code=f'ASC-{i+1:04d}',
                gender=gender,
                phone=f'9770{i+1:04d}',
                email=f'{first_name.lower()}.{last_name.lower()}@asc.local',
                site=site,
                zone_asc=zones[i % len(zones)],
                supervisor=sup,
                is_active=True
            )
            ascs.append(asc)

        # Créer les équipements
        self.stdout.write('Création des équipements...')
        brands = ['Samsung', 'Tecno', 'Infinix', 'Nokia']
        models = ['Galaxy A12', 'Spark 7', 'Hot 10', '105']
        equipments = []

        for i, asc in enumerate(ascs):
            for j in range(random.randint(1, 2)):
                equipment = Equipment.objects.create(
                    equipment_type='PHONE',
                    brand=random.choice(brands),
                    model=random.choice(models),
                    imei=f'35{random.randint(100000000000, 999999999999)}',
                    owner=asc,
                    status=random.choice(['FUNCTIONAL', 'FUNCTIONAL', 'FAULTY', 'UNDER_REPAIR']),
                    acquisition_date=timezone.now().date() - timedelta(days=random.randint(30, 365))
                )
                equipments.append(equipment)

        # Créer des tickets de réparation
        self.stdout.write('Création des tickets de réparation...')
        faulty_equipments = [e for e in equipments if e.status in ['FAULTY', 'UNDER_REPAIR']]

        stages = ['SUPERVISOR', 'PROGRAM', 'LOGISTICS', 'REPAIRER', 'ESANTE']
        statuses = ['OPEN', 'IN_PROGRESS', 'IN_PROGRESS', 'REPAIRED']

        for i, equipment in enumerate(faulty_equipments[:15]):  # Créer 15 tickets
            days_ago = random.randint(1, 30)
            initial_date = timezone.now() - timedelta(days=days_ago)

            ticket = RepairTicket.objects.create(
                equipment=equipment,
                asc=equipment.owner,
                status=random.choice(statuses),
                priority=random.choice(['LOW', 'NORMAL', 'NORMAL', 'HIGH']),
                current_stage=random.choice(stages),
                current_holder=random.choice([superviseur1, programme, logistique, esante, reparateur]),
                initial_send_date=initial_date,
                created_by=equipment.owner.supervisor,
                initial_problem_description=random.choice([
                    'Écran cassé suite à une chute',
                    'Batterie ne tient plus la charge',
                    'Problème de réseau, pas de signal',
                    'Applications qui plantent régulièrement',
                    'Téléphone ne s\'allume plus',
                    'Problème de son, micro ne fonctionne pas',
                ])
            )

            # Créer des issues
            issue_types = ['HARDWARE'] if i % 2 == 0 else ['SOFTWARE']
            for issue_type in issue_types:
                Issue.objects.create(
                    ticket=ticket,
                    issue_type=issue_type,
                    description=f'Problème de type {issue_type}'
                )

            # Créer quelques événements
            event_date = initial_date
            TicketEvent.objects.create(
                ticket=ticket,
                event_type='CREATED',
                from_role='SUPERVISOR',
                to_role='SUPERVISOR',
                user=equipment.owner.supervisor,
                timestamp=event_date,
                comment='Ticket créé'
            )

            # Ajouter des événements aléatoires
            if days_ago > 3:
                event_date += timedelta(days=1)
                TicketEvent.objects.create(
                    ticket=ticket,
                    event_type='SENT',
                    from_role='SUPERVISOR',
                    to_role='PROGRAM',
                    user=equipment.owner.supervisor,
                    timestamp=event_date,
                    comment='Envoyé au département Programme'
                )

            if days_ago > 7:
                event_date += timedelta(days=2)
                TicketEvent.objects.create(
                    ticket=ticket,
                    event_type='RECEIVED',
                    from_role='SUPERVISOR',
                    to_role='PROGRAM',
                    user=programme,
                    timestamp=event_date,
                    comment='Reçu par le Programme'
                )

        self.stdout.write(self.style.SUCCESS('Données de démonstration créées avec succès!'))
        self.stdout.write(self.style.SUCCESS(f'- {Region.objects.count()} régions'))
        self.stdout.write(self.style.SUCCESS(f'- {District.objects.count()} districts'))
        self.stdout.write(self.style.SUCCESS(f'- {Site.objects.count()} sites'))
        self.stdout.write(self.style.SUCCESS(f'- {ZoneASC.objects.count()} zones ASC'))
        self.stdout.write(self.style.SUCCESS(f'- {User.objects.count()} utilisateurs'))
        self.stdout.write(self.style.SUCCESS(f'- {ASC.objects.count()} ASCs'))
        self.stdout.write(self.style.SUCCESS(f'- {Equipment.objects.count()} équipements'))
        self.stdout.write(self.style.SUCCESS(f'- {RepairTicket.objects.count()} tickets de réparation'))

        self.stdout.write(self.style.SUCCESS('\nComptes de test:'))
        self.stdout.write('  admin / admin123 (Administrateur)')
        self.stdout.write('  superviseur1 / pass123 (Superviseur)')
        self.stdout.write('  programme / pass123 (Programme)')
        self.stdout.write('  logistique / pass123 (Logistique)')
        self.stdout.write('  esante / pass123 (E-Santé)')
        self.stdout.write('  reparateur / pass123 (Réparateur)')
