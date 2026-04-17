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


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
