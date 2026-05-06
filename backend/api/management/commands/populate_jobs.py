from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal
from api.models import JobOffer, Profile


class Command(BaseCommand):
    help = 'Populate database with sample job offers'

    def handle(self, *args, **options):
        # Create or get a client user
        client_user, created = User.objects.get_or_create(
            username='client_demo',
            defaults={
                'email': 'client@tunifreelance.com',
                'first_name': 'Ahmed',
                'last_name': 'Khalil',
            }
        )

        if created:
            client_user.set_password('password123')
            client_user.save()
            # Profile is automatically created via signal
            profile, _ = Profile.objects.get_or_create(user=client_user)
            profile.role = Profile.ROLE_CLIENT
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Created client user: {client_user.username}'))
        else:
            self.stdout.write(f'Client user already exists: {client_user.username}')
            # Update profile to client role if needed
            profile, _ = Profile.objects.get_or_create(user=client_user)
            if profile.role != Profile.ROLE_CLIENT:
                profile.role = Profile.ROLE_CLIENT
                profile.save()
                self.stdout.write(f'Updated {client_user.username} profile to client role')
        # Sample job offers
        job_offers = [
            {
                'title': 'Développement site e-commerce React',
                'category': 'Développement Web',
                'description': 'Nous cherchons un développeur React expérimenté pour construire un site e-commerce moderne avec panier d\'achat, paiement intégré et gestion d\'inventaire. Le projet doit être responsive et optimisé pour les performances.',
                'budget': Decimal('1200.00'),
                'deadline_days': 30,
            },
            {
                'title': 'Design graphique - Logo et identité visuelle',
                'category': 'Design',
                'description': 'Création d\'un logo moderne et d\'une identité visuelle pour une startup tech. Nous avons besoin de 3-4 concepts différents avec palette de couleurs et guide de style.',
                'budget': Decimal('400.00'),
                'deadline_days': 14,
            },
            {
                'title': 'Développement API REST Node.js',
                'category': 'Développement Backend',
                'description': 'Développement d\'une API REST complète avec Node.js et Express. L\'API doit inclure authentification JWT, validation des données, documentation Swagger et tests unitaires.',
                'budget': Decimal('1500.00'),
                'deadline_days': 45,
            },
            {
                'title': 'Campagne marketing digital et SEO',
                'category': 'Marketing Digital',
                'description': 'Gérer une campagne marketing complète incluant: audit SEO, optimisation des mots-clés, création de contenu, gestion des réseaux sociaux et rapports mensuels.',
                'budget': Decimal('800.00'),
                'deadline_days': 60,
            },
            {
                'title': 'Rédaction contenu blog - 10 articles',
                'category': 'Rédaction',
                'description': 'Rédaction de 10 articles de blog de 1500 mots chacun sur des sujets tech. Les articles doivent être optimisés SEO, engageants et bien structurés.',
                'budget': Decimal('500.00'),
                'deadline_days': 30,
            },
            {
                'title': 'Traduction EN-FR de documentation technique',
                'category': 'Traduction',
                'description': 'Traduction professionnelle de 50 pages de documentation technique de l\'anglais vers le français. Connaissance en terminologie tech requise.',
                'budget': Decimal('600.00'),
                'deadline_days': 21,
            },
            {
                'title': 'Développement application mobile iOS Swift',
                'category': 'Développement Mobile',
                'description': 'Développement d\'une application iOS avec SwiftUI. L\'app doit inclure une authentification sécurisée, synchronisation avec backend et Interface utilisateur intuitive.',
                'budget': Decimal('2000.00'),
                'deadline_days': 60,
            },
            {
                'title': 'Intégration paiement Stripe et PayPal',
                'category': 'Développement Web',
                'description': 'Intégration des systèmes de paiement Stripe et PayPal dans une application web existante. Gestion des webhooks et des erreurs de paiement requise.',
                'budget': Decimal('350.00'),
                'deadline_days': 10,
            },
            {
                'title': 'Création vidéo promotionnelle - 60 secondes',
                'category': 'Vidéo',
                'description': 'Production d\'une vidéo promotionnelle professionnelle de 60 secondes pour présenter notre produit. Inclut scénarisation, tournage et montage haute qualité.',
                'budget': Decimal('900.00'),
                'deadline_days': 25,
            },
            {
                'title': 'Audit de sécurité code et infrastructure',
                'category': 'Cybersécurité',
                'description': 'Audit de sécurité complet: revue du code, scan des vulnérabilités, test de pénétration et recommandations. Rapport détaillé requis.',
                'budget': Decimal('1800.00'),
                'deadline_days': 40,
            },
            {
                'title': 'Gestion base de données PostgreSQL',
                'category': 'Base de Données',
                'description': 'Optimisation et gestion d\'une base de données PostgreSQL pour une application haute performance. Incluant indexation, requêtes optimisées et backup automation.',
                'budget': Decimal('700.00'),
                'deadline_days': 20,
            },
            {
                'title': 'Community management - 3 mois',
                'category': 'Social Media',
                'description': 'Gestion complète des réseaux sociaux (Instagram, LinkedIn, Twitter) pendant 3 mois. Création de contenu, engagement avec la communauté et rapports mensuels.',
                'budget': Decimal('900.00'),
                'deadline_days': 90,
            },
            {
                'title': 'Développement chatbot IA avec GPT',
                'category': 'IA/Machine Learning',
                'description': 'Créer un chatbot intelligent utilisant OpenAI GPT pour le support client. Intégration web, modération de contenu et analytics inclus.',
                'budget': Decimal('1100.00'),
                'deadline_days': 35,
            },
            {
                'title': 'Refactorisation code legacy Python',
                'category': 'Développement Backend',
                'description': 'Refactorisation d\'une codebase Python legacy pour améliorer la maintenabilité, les performances et les tests. Documentation comprise.',
                'budget': Decimal('850.00'),
                'deadline_days': 30,
            },
            {
                'title': 'Template WordPress personnalisé',
                'category': 'WordPress',
                'description': 'Développement d\'un thème WordPress custom avec WooCommerce intégré. Responsive, optimisé SEO et performances. Code propre et documenté.',
                'budget': Decimal('650.00'),
                'deadline_days': 25,
            },
        ]

        created_count = 0
        for job_data in job_offers:
            deadline = datetime.now().date() + timedelta(days=job_data.pop('deadline_days'))

            job_offer, created = JobOffer.objects.get_or_create(
                client=client_user,
                title=job_data['title'],
                defaults={
                    'category': job_data['category'],
                    'description': job_data['description'],
                    'budget': job_data['budget'],
                    'deadline': deadline,
                    'status': JobOffer.STATUS_OPEN,
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Created: {job_data["title"]}')
            else:
                self.stdout.write(f'  → Already exists: {job_data["title"]}')

        self.stdout.write(
            self.style.SUCCESS(f'\n✅ Successfully added {created_count} job offers!')
        )
