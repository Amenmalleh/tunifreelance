from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CLIENT = 'client'
    ROLE_FREELANCER = 'freelancer'
    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Client'),
        (ROLE_FREELANCER, 'Freelancer'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_FREELANCER)

    def __str__(self):
        return f'{self.user.username} ({self.role})'


class JobOffer(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Ouvert'),
        (STATUS_CLOSED, 'Fermé'),
    ]

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_offers')
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    deadline = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.client.username})'


class Proposal(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'En attente'),
        (STATUS_ACCEPTED, 'Accepté'),
        (STATUS_REJECTED, 'Refusé'),
    ]

    freelance = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proposals')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='proposals')
    message = models.TextField()
    proposed_price = models.DecimalField(max_digits=10, decimal_places=2)
    proposed_deadline = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Proposal by {self.freelance.username} for {self.job_offer.title}'


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender.username} to {self.recipient.username}'


class Contract(models.Model):
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Actif'),
        (STATUS_COMPLETED, 'Complété'),
        (STATUS_CANCELLED, 'Annulé'),
    ]

    proposal = models.OneToOneField(Proposal, on_delete=models.CASCADE, related_name='contract')
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='contracts')
    freelancer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='active_contracts')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='issued_contracts')
    
    contract_price = models.DecimalField(max_digits=10, decimal_places=2)  # Final agreed price
    contract_deadline = models.DateField()  # Final agreed deadline
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    amount_locked = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount blocked until completion
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Contract: {self.job_offer.title} - {self.freelancer.username}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('proposal_received', 'Nouvelle proposition reçue'),
        ('proposal_accepted', 'Proposition acceptée'),
        ('proposal_rejected', 'Proposition rejetée'),
        ('message_received', 'Nouveau message'),
        ('contract_created', 'Contrat créé'),
        ('contract_completed', 'Contrat complété'),
        ('contract_cancelled', 'Contrat annulé'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)  # Frontend route to navigate to
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Notification for {self.user.username}: {self.title}'


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
