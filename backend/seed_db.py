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
        {'client': 'john_client', 'title': 'SEO Optimization', 'category': 'Marketing', 'location': 'New York, USA', 'description': 'Looking for an SEO expert to improve our search rankings.', 'budget': '500.00', 'deadline': date.today() + timedelta(days=20)}
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
