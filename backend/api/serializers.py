from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from .models import Profile, JobOffer, Proposal, Message, Contract


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=Profile.ROLE_CHOICES, write_only=True, required=False, default=Profile.ROLE_FREELANCER)

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'password2', 'email', 'first_name', 'last_name', 'role')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role', Profile.ROLE_FREELANCER)
        validated_data.pop('password2', None)

        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        Profile.objects.update_or_create(user=user, defaults={'role': role})
        return user

    def to_representation(self, instance):
        profile, _ = Profile.objects.get_or_create(user=instance)
        representation = super().to_representation(instance)
        representation['role'] = profile.role
        return representation


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, error_messages={'required': 'Ce champ est obligatoire.'})
    password = serializers.CharField(required=True, error_messages={'required': 'Le mot de passe est obligatoire.'})


class JobOfferSerializer(serializers.ModelSerializer):
    client = serializers.ReadOnlyField(source='client.username')
    client_role = serializers.CharField(source='client.profile.role', read_only=True)

    class Meta:
        model = JobOffer
        fields = (
            'id', 'client', 'client_role', 'title', 'category', 'description',
            'budget', 'deadline', 'status', 'skills_required', 'experience_level',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'client', 'client_role', 'created_at', 'updated_at')


class ProposalSerializer(serializers.ModelSerializer):
    freelance = serializers.ReadOnlyField(source='freelance.username')
    freelance_role = serializers.CharField(source='freelance.profile.role', read_only=True)
    job_offer_title = serializers.CharField(source='job_offer.title', read_only=True)

    class Meta:
        model = Proposal
        fields = ('id', 'freelance', 'freelance_role', 'job_offer', 'job_offer_title', 'message', 'proposed_price', 'proposed_deadline', 'status', 'created_at')
        read_only_fields = ('id', 'freelance', 'freelance_role', 'job_offer_title', 'status', 'created_at')


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.username')
    recipient = serializers.ReadOnlyField(source='recipient.username')
    sender_id = serializers.CharField(source='sender.id', read_only=True)
    recipient_id = serializers.CharField(source='recipient.id', read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_id', 'recipient', 'recipient_id', 'proposal', 'job_offer', 'content', 'created_at', 'is_read')
        read_only_fields = ('id', 'sender', 'sender_id', 'recipient', 'recipient_id', 'created_at')


class ContractSerializer(serializers.ModelSerializer):
    freelancer = serializers.ReadOnlyField(source='freelancer.username')
    client = serializers.ReadOnlyField(source='client.username')
    job_title = serializers.CharField(source='job_offer.title', read_only=True)
    proposal_details = ProposalSerializer(source='proposal', read_only=True)

    class Meta:
        model = Contract
        fields = ('id', 'proposal', 'job_offer', 'freelancer', 'client', 'job_title', 'contract_price', 'contract_deadline', 'status', 'amount_locked', 'is_completed', 'proposal_details', 'created_at', 'completed_at')
        read_only_fields = ('id', 'freelancer', 'client', 'job_title', 'created_at', 'completed_at', 'proposal_details')
