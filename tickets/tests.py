from django.test import TestCase
from django.utils import timezone
from accounts.models import User, ASC
from locations.models import Region, District, Site
from assets.models import Equipment
from .models import RepairTicket, Issue, TicketEvent


class RepairTicketModelTest(TestCase):
    def setUp(self):
        """Créer des données de test"""
        # Créer la hiérarchie géographique
        region = Region.objects.create(name='Test Region', code='TR')
        district = District.objects.create(region=region, name='Test District', code='TD')
        site = Site.objects.create(
            district=district,
            name='Test Site',
            code='TS'
        )

        # Créer un superviseur
        self.supervisor = User.objects.create_user(
            username='testsupervisor',
            password='testpass',
            role='SUPERVISOR',
            site=site
        )

        # Créer un ASC
        self.asc = ASC.objects.create(
            first_name='Test',
            last_name='ASC',
            code='ASC-TEST',
            phone='97000000',
            site=site,
            supervisor=self.supervisor
        )

        # Créer un équipement
        self.equipment = Equipment.objects.create(
            equipment_type='PHONE',
            brand='Test Brand',
            model='Test Model',
            imei='123456789',
            owner=self.asc,
            status='FAULTY'
        )

    def test_ticket_creation(self):
        """Test création d'un ticket"""
        ticket = RepairTicket.objects.create(
            equipment=self.equipment,
            asc=self.asc,
            created_by=self.supervisor,
            initial_problem_description='Test problem'
        )

        self.assertIsNotNone(ticket.ticket_number)
        self.assertEqual(ticket.status, 'OPEN')
        self.assertEqual(ticket.current_stage, 'SUPERVISOR')

    def test_ticket_delay_color(self):
        """Test calcul de la couleur selon le délai"""
        ticket = RepairTicket.objects.create(
            equipment=self.equipment,
            asc=self.asc,
            created_by=self.supervisor,
            initial_problem_description='Test problem'
        )

        # Ticket récent devrait être vert
        self.assertEqual(ticket.get_delay_color(), 'success')

    def test_issue_creation(self):
        """Test création d'un problème"""
        ticket = RepairTicket.objects.create(
            equipment=self.equipment,
            asc=self.asc,
            created_by=self.supervisor,
            initial_problem_description='Test problem'
        )

        issue = Issue.objects.create(
            ticket=ticket,
            issue_type='HARDWARE',
            description='Écran cassé'
        )

        self.assertEqual(issue.ticket, ticket)
        self.assertEqual(issue.issue_type, 'HARDWARE')


class TicketEventModelTest(TestCase):
    def setUp(self):
        """Créer des données de test"""
        region = Region.objects.create(name='Test Region', code='TR')
        district = District.objects.create(region=region, name='Test District', code='TD')
        site = Site.objects.create(district=district, name='Test Site', code='TS')

        self.supervisor = User.objects.create_user(
            username='testsupervisor',
            password='testpass',
            role='SUPERVISOR',
            site=site
        )

        self.asc = ASC.objects.create(
            first_name='Test',
            last_name='ASC',
            code='ASC-TEST',
            phone='97000000',
            site=site,
            supervisor=self.supervisor
        )

        self.equipment = Equipment.objects.create(
            equipment_type='PHONE',
            brand='Test Brand',
            model='Test Model',
            imei='123456789',
            owner=self.asc,
            status='FAULTY'
        )

        self.ticket = RepairTicket.objects.create(
            equipment=self.equipment,
            asc=self.asc,
            created_by=self.supervisor,
            initial_problem_description='Test problem'
        )

    def test_event_creation(self):
        """Test création d'un événement"""
        event = TicketEvent.objects.create(
            ticket=self.ticket,
            event_type='CREATED',
            user=self.supervisor,
            from_role='SUPERVISOR',
            to_role='SUPERVISOR',
            comment='Ticket créé'
        )

        self.assertEqual(event.ticket, self.ticket)
        self.assertEqual(event.event_type, 'CREATED')
        self.assertEqual(event.user, self.supervisor)
