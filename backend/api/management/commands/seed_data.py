import random
from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from faker import Faker

from api.models import Contract, JobOffer, Profile, Proposal, Rating

fake = Faker('fr_FR')

CATEGORIES = [
    'Développement Web', 'Design Graphique', 'Montage Vidéo',
    'Marketing Digital', 'Rédaction', 'Mobile', 'SEO', 'Data Science',
]

JOB_TITLES = [
    'Développement site e-commerce', 'Logo pour startup tech',
    'Montage vidéo TikTok promotionnel', 'Application mobile Flutter',
    'Refonte site WordPress', 'Identité visuelle complète',
    'Campagne publicitaire Facebook Ads', 'Développement API REST Django',
    'Création landing page moderne', 'Animation motion design',
    'Audit SEO et optimisation', 'Tableau de bord analytique React',
    'Rédaction articles de blog SEO', 'Application de gestion RH',
    'Intégration maquette Figma', 'Bot Telegram automatisé',
    'Dashboard Power BI', 'Formation Python débutant',
    'Script scraping données', 'Chatbot service client',
    'Redesign UX application mobile', 'Plugin WordPress sur mesure',
]

PROPOSAL_MESSAGES = [
    "Bonjour, je suis très intéressé par ce projet. J'ai une expérience solide dans ce domaine et je peux livrer un travail de qualité dans les délais.",
    "Je dispose de toutes les compétences requises pour mener à bien ce projet. Mon portfolio témoigne de mes réalisations similaires.",
    "Ce projet correspond parfaitement à mon expertise. Je propose une approche structurée avec des livrables clairs à chaque étape.",
    "Avec plus de 3 ans d'expérience dans ce domaine, je suis confiant dans ma capacité à répondre à vos attentes.",
    "Votre projet est très intéressant. Je propose une méthodologie agile avec des points d'avancement réguliers.",
    "Je travaille sur des projets similaires depuis plusieurs années. Je garantis la qualité et le respect des délais.",
    "Professionnel certifié avec de nombreuses références clients, je peux démarrer immédiatement.",
]

RATING_COMMENTS = [
    "Excellent travail, très professionnel et réactif.",
    "Bonne communication et livraison dans les délais.",
    "Travail de qualité, je recommande vivement.",
    "Très satisfait du résultat final, conforme aux attentes.",
    "Freelancer sérieux et compétent, bonne expérience.",
    "Quelques retards mais résultat final satisfaisant.",
    "Communication parfaite et code bien structuré.",
]


class Command(BaseCommand):
    help = 'Remplit la base de données avec des données de test réalistes'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Nettoyage des données existantes de test...'))
        self._clean_test_data()

        self.stdout.write(self.style.HTTP_INFO('Création des utilisateurs...'))
        clients = self._create_clients()
        freelancers = self._create_freelancers()

        self.stdout.write(self.style.HTTP_INFO('Création des offres de travail...'))
        jobs = self._create_jobs(clients)

        self.stdout.write(self.style.HTTP_INFO('Création des propositions...'))
        proposals = self._create_proposals(jobs, freelancers)

        self.stdout.write(self.style.HTTP_INFO('Création des contrats...'))
        contracts = self._create_contracts(proposals)

        self.stdout.write(self.style.HTTP_INFO('Création des évaluations...'))
        self._create_ratings(contracts)

        self._print_summary(clients, freelancers)

    def _clean_test_data(self):
        test_usernames = (
            [f'client{i}' for i in range(1, 6)] +
            [f'freelancer{i}' for i in range(1, 11)]
        )
        User.objects.filter(username__in=test_usernames).delete()

    def _create_clients(self):
        clients = []
        for i in range(1, 6):
            user = User.objects.create_user(
                username=f'client{i}',
                email=f'client{i}@test.com',
                password='Test1234',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            Profile.objects.update_or_create(user=user, defaults={'role': Profile.ROLE_CLIENT})
            clients.append(user)
        return clients

    def _create_freelancers(self):
        freelancers = []
        for i in range(1, 11):
            user = User.objects.create_user(
                username=f'freelancer{i}',
                email=f'freelancer{i}@test.com',
                password='Test1234',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
            )
            Profile.objects.update_or_create(user=user, defaults={'role': Profile.ROLE_FREELANCER})
            freelancers.append(user)
        return freelancers

    def _create_jobs(self, clients):
        jobs = []
        titles = random.sample(JOB_TITLES, min(len(JOB_TITLES), 22))
        for i, title in enumerate(titles):
            client = clients[i % len(clients)]
            budget = round(random.uniform(200, 5000), 2)
            deadline = date.today() + timedelta(days=random.randint(3, 60))
            status = JobOffer.STATUS_OPEN if i < 18 else JobOffer.STATUS_CLOSED
            job = JobOffer.objects.create(
                client=client,
                title=title,
                category=random.choice(CATEGORIES),
                description=fake.paragraph(nb_sentences=4),
                budget=budget,
                deadline=deadline,
                status=status,
            )
            jobs.append(job)
        return jobs

    def _create_proposals(self, jobs, freelancers):
        proposals = []
        for job in jobs:
            nb_proposals = random.randint(1, 5)
            selected_freelancers = random.sample(freelancers, min(nb_proposals, len(freelancers)))
            for freelancer in selected_freelancers:
                variation = random.uniform(0.80, 1.20)
                price = round(float(job.budget) * variation, 2)
                delay_days = random.randint(-5, 10)
                proposed_deadline = job.deadline + timedelta(days=delay_days)
                proposal = Proposal.objects.create(
                    freelance=freelancer,
                    job_offer=job,
                    message=random.choice(PROPOSAL_MESSAGES),
                    proposed_price=price,
                    proposed_deadline=proposed_deadline,
                    status=Proposal.STATUS_PENDING,
                )
                proposals.append(proposal)
        return proposals

    def _create_contracts(self, proposals):
        contracts = []
        # Regroup proposals by job
        proposals_by_job = {}
        for p in proposals:
            proposals_by_job.setdefault(p.job_offer_id, []).append(p)

        contract_count = 0
        statuses_pool = (
            [Contract.STATUS_COMPLETED] * 6 +
            [Contract.STATUS_ACTIVE] * 3 +
            [Contract.STATUS_CANCELLED] * 1
        )

        for job_id, job_proposals in proposals_by_job.items():
            if contract_count >= 12:
                break
            chosen = random.choice(job_proposals)
            # Skip if proposal already has a contract
            if hasattr(chosen, 'contract'):
                continue
            contract_status = statuses_pool[contract_count % len(statuses_pool)]
            contract = Contract.objects.create(
                proposal=chosen,
                job_offer=chosen.job_offer,
                freelancer=chosen.freelance,
                client=chosen.job_offer.client,
                contract_price=chosen.proposed_price,
                contract_deadline=chosen.proposed_deadline or chosen.job_offer.deadline,
                status=contract_status,
                amount_locked=chosen.proposed_price,
                is_completed=(contract_status == Contract.STATUS_COMPLETED),
            )
            chosen.status = Proposal.STATUS_ACCEPTED
            chosen.save(update_fields=['status'])
            # Reject other proposals for this job
            Proposal.objects.filter(
                job_offer=chosen.job_offer,
                status=Proposal.STATUS_PENDING,
            ).exclude(pk=chosen.pk).update(status=Proposal.STATUS_REJECTED)
            contracts.append(contract)
            contract_count += 1
        return contracts

    def _create_ratings(self, contracts):
        completed = [c for c in contracts if c.status == Contract.STATUS_COMPLETED]
        for contract in completed:
            if Rating.objects.filter(contract=contract).exists():
                continue
            Rating.objects.create(
                contract=contract,
                client=contract.client,
                freelancer=contract.freelancer,
                score=random.randint(3, 5),
                comment=random.choice(RATING_COMMENTS),
            )

    def _print_summary(self, clients, freelancers):
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.SUCCESS('   SEED TERMINÉ — Comptes de test créés'))
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write(self.style.WARNING('CLIENTS (role: client)'))
        for c in clients:
            self.stdout.write(f'  • {c.email}  /  Test1234')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('FREELANCERS (role: freelancer)'))
        for f in freelancers:
            self.stdout.write(f'  • {f.email}  /  Test1234')
        self.stdout.write(self.style.SUCCESS('=' * 55))
        self.stdout.write('')
        jobs_count = JobOffer.objects.filter(
            client__username__startswith='client'
        ).count()
        proposals_count = Proposal.objects.filter(
            freelance__username__startswith='freelancer'
        ).count()
        contracts_count = Contract.objects.filter(
            freelancer__username__startswith='freelancer'
        ).count()
        ratings_count = Rating.objects.filter(
            freelancer__username__startswith='freelancer'
        ).count()
        self.stdout.write(f'  Jobs créés       : {jobs_count}')
        self.stdout.write(f'  Propositions     : {proposals_count}')
        self.stdout.write(f'  Contrats         : {contracts_count}')
        self.stdout.write(f'  Évaluations      : {ratings_count}')
        self.stdout.write('')
