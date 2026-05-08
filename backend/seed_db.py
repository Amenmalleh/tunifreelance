import os
import django
from decimal import Decimal
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from api.models import Profile, JobOffer, Proposal, Message

def seed():
    print("Clearing existing test data...")
    User.objects.exclude(is_superuser=True).delete()

    print("Creating test users...")
    users_data = [
        {'username': 'john_client', 'email': 'john@example.com', 'first_name': 'John', 'last_name': 'Doe', 'role': 'client', 'location': 'New York, USA'},
        {'username': 'jane_client', 'email': 'jane@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'role': 'client', 'location': 'London, UK'},
        {'username': 'mohamedali', 'email': 'mohamed@example.com', 'first_name': 'Mohamed', 'last_name': 'Ali', 'role': 'freelancer', 'location': 'Tunis, Tunisia'},
        {'username': 'amirabenromdhane', 'email': 'amira@example.com', 'first_name': 'Amira', 'last_name': 'Ben Romdhane', 'role': 'freelancer', 'location': 'Sousse, Tunisia'},
        {'username': 'yassinemansour', 'email': 'yassine@example.com', 'first_name': 'Yassine', 'last_name': 'Mansour', 'role': 'freelancer', 'location': 'Sfax, Tunisia'}
    ]

    users = {}
    for data in users_data:
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password='password123',
            first_name=data['first_name'],
            last_name=data['last_name']
        )
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = data['role']
        profile.location = data['location']
        profile.save()
        users[data['username']] = user
    print("Users created.")

    print("Creating job offers...")
    jobs_data = [
        {'client': 'john_client', 'title': 'E-commerce Website Development', 'category': 'Development', 'location': 'Remote', 'description': 'Looking for an experienced full-stack developer to build a modern e-commerce website.', 'budget': '1500.00', 'deadline': date.today() + timedelta(days=30)},
        {'client': 'jane_client', 'title': 'Logo Design for Startup', 'category': 'Design', 'location': 'London, UK', 'description': 'Need a creative UI/UX designer to create a modern logo and brand identity.', 'budget': '300.00', 'deadline': date.today() + timedelta(days=15)},
        {'client': 'john_client', 'title': 'SEO Optimization', 'category': 'Marketing', 'location': 'New York, USA', 'description': 'Looking for an SEO expert to improve our search rankings.', 'budget': '500.00', 'deadline': date.today() + timedelta(days=20)},
        {'client': 'jane_client', 'title': 'Mobile App Development', 'category': 'Development', 'location': 'San Francisco, USA', 'description': 'Need a developer to build a cross-platform mobile app for our delivery service.', 'budget': '2500.00', 'deadline': date.today() + timedelta(days=45)},
        {'client': 'john_client', 'title': 'Copywriting for Tech Blog', 'category': 'Writing', 'location': 'Remote', 'description': 'Looking for a technical writer to write 4 articles per month on AI and web development.', 'budget': '400.00', 'deadline': date.today() + timedelta(days=60)},
        {'client': 'jane_client', 'title': 'Video Editing for YouTube Channel', 'category': 'Video & Animation', 'location': 'Los Angeles, USA', 'description': 'Need a skilled video editor to edit weekly vlogs and tech reviews.', 'budget': '800.00', 'deadline': date.today() + timedelta(days=14)},
        {'client': 'john_client', 'title': 'Customer Support Representative', 'category': 'Customer Service', 'location': 'Manila, Philippines', 'description': 'Looking for an English-speaking customer support agent for email and chat support.', 'budget': '600.00', 'deadline': date.today() + timedelta(days=30)},
        {'client': 'jane_client', 'title': 'Data Analysis using Python', 'category': 'Data Science', 'location': 'Berlin, Germany', 'description': 'Need a data analyst to analyze our sales data and create a dashboard using pandas and Dash.', 'budget': '1200.00', 'deadline': date.today() + timedelta(days=21)},
        {'client': 'john_client', 'title': 'Social Media Manager', 'category': 'Marketing', 'location': 'Dubai, UAE', 'description': 'Looking for a manager to handle Instagram, Twitter, and LinkedIn accounts.', 'budget': '700.00', 'deadline': date.today() + timedelta(days=90)},
        {'client': 'jane_client', 'title': 'Translate Website to French', 'category': 'Translation', 'location': 'Paris, France', 'description': 'Need a native French speaker to translate our corporate website from English to French.', 'budget': '450.00', 'deadline': date.today() + timedelta(days=10)},
        {'client': 'john_client', 'title': '3D Modeling for Game Assets', 'category': 'Design', 'location': 'Tokyo, Japan', 'description': 'Looking for a 3D artist to create low-poly models for an upcoming mobile game.', 'budget': '2000.00', 'deadline': date.today() + timedelta(days=60)},
    ]
    
    jobs = []
    for data in jobs_data:
        job = JobOffer.objects.create(
            client=users[data['client']],
            title=data['title'],
            category=data['category'],
            location=data['location'],
            description=data['description'],
            budget=Decimal(data['budget']),
            deadline=data['deadline']
        )
        jobs.append(job)
    print("Job offers created.")

    print("Creating proposals...")
    proposal = Proposal.objects.create(
        freelance=users['mohamedali'],
        job_offer=jobs[0],
        message='Hello, I have extensive experience building scalable e-commerce solutions. I would love to work on this project.',
        proposed_price=Decimal('1400.00'),
        proposed_deadline=date.today() + timedelta(days=25)
    )

    Proposal.objects.create(
        freelance=users['amirabenromdhane'],
        job_offer=jobs[1],
        message='Hi, I am a UI/UX designer with a focus on modern branding. Check out my portfolio!',
        proposed_price=Decimal('250.00'),
        proposed_deadline=date.today() + timedelta(days=10)
    )
    print("Proposals created.")

    print("Creating messages...")
    Message.objects.create(
        sender=users['john_client'],
        recipient=users['mohamedali'],
        proposal=proposal,
        job_offer=jobs[0],
        content='Hi Mohamed, I liked your proposal. Can we discuss some technical details?',
    )
    Message.objects.create(
        sender=users['mohamedali'],
        recipient=users['john_client'],
        proposal=proposal,
        job_offer=jobs[0],
        content='Hello John, sure! I am available right now. Let me know what you have in mind.',
    )
    print("Messages created.")
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
