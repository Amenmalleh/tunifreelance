from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import filters, status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, JobOffer, Proposal, Message, Contract
from .serializers import UserSerializer, LoginSerializer, JobOfferSerializer, ProposalSerializer, MessageSerializer, ContractSerializer


class SignupView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        identifier = serializer.validated_data['identifier'].strip()
        password   = serializer.validated_data['password']
        _bad_creds = Response(
            {'error': 'Identifiant ou mot de passe incorrect.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

        # Résolution email → username
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email__iexact=identifier)
                username = user_obj.username
            except User.DoesNotExist:
                return _bad_creds
        else:
            username = identifier

        user = authenticate(username=username, password=password)
        if not user:
            return _bad_creds

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=request.user)
        return profile.role == Profile.ROLE_CLIENT


class IsFreelance(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        profile = getattr(request.user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=request.user)
        return profile.role == Profile.ROLE_FREELANCER


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.client == request.user


class IsProposalOwnerOrClient(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.freelance == request.user or obj.job_offer.client == request.user


class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'category']

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsClient()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsClient(), IsOwnerOrReadOnly()]
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = JobOffer.objects.select_related('client', 'client__profile')
        user = self.request.user

        if not user.is_authenticated:
            queryset = queryset.filter(status=JobOffer.STATUS_OPEN)
        else:
            profile = getattr(user, 'profile', None)
            if profile is None:
                profile, _ = Profile.objects.get_or_create(user=user)
            if profile.role == Profile.ROLE_FREELANCER:
                queryset = queryset.filter(status=JobOffer.STATUS_OPEN)
            else:
                queryset = queryset.filter(Q(status=JobOffer.STATUS_OPEN) | Q(client=user))

        category = self.request.query_params.get('category', '').strip()
        if category:
            queryset = queryset.filter(category__icontains=category)

        return queryset

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


class ProposalViewSet(viewsets.ModelViewSet):
    queryset = Proposal.objects.all()
    serializer_class = ProposalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsFreelance()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsProposalOwnerOrClient()]
        if self.action in ['accept', 'reject']:
            return [permissions.IsAuthenticated(), IsClient()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role == Profile.ROLE_FREELANCER:
            return Proposal.objects.filter(freelance=user).select_related('job_offer', 'freelance')
        return Proposal.objects.filter(job_offer__client=user).select_related('job_offer', 'freelance')

    def perform_create(self, serializer):
        serializer.save(freelance=self.request.user)

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        with transaction.atomic():
            proposal = Proposal.objects.select_for_update().select_related('job_offer', 'freelance').get(pk=pk)

            if proposal.job_offer.client != request.user:
                return Response(
                    {'error': 'Only the job client can accept proposals'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if proposal.status != Proposal.STATUS_PENDING:
                return Response(
                    {'error': f'Can only accept pending proposals. Current status: {proposal.status}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if hasattr(proposal, 'contract'):
                return Response(
                    {'error': 'A contract already exists for this proposal'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            contract = Contract.objects.create(
                proposal=proposal,
                job_offer=proposal.job_offer,
                freelancer=proposal.freelance,
                client=request.user,
                contract_price=proposal.proposed_price,
                contract_deadline=proposal.proposed_deadline or proposal.job_offer.deadline,
                amount_locked=proposal.proposed_price
            )

            proposal.status = Proposal.STATUS_ACCEPTED
            proposal.save(update_fields=['status'])

            Proposal.objects.filter(
                job_offer=proposal.job_offer,
                status=Proposal.STATUS_PENDING
            ).exclude(pk=proposal.pk).update(status=Proposal.STATUS_REJECTED)

            proposal.job_offer.status = JobOffer.STATUS_CLOSED
            proposal.job_offer.save(update_fields=['status'])

        return Response({
            'message': 'Proposal accepted successfully',
            'contract': ContractSerializer(contract).data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        proposal = self.get_object()
        
        # Verify that the requester is the job client
        if proposal.job_offer.client != request.user:
            return Response(
                {'error': 'Only the job client can reject proposals'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if proposal.status != Proposal.STATUS_PENDING:
            return Response(
                {'error': f'Can only reject pending proposals. Current status: {proposal.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        proposal.status = Proposal.STATUS_REJECTED
        proposal.save()

        return Response({
            'message': 'Proposal rejected successfully',
            'proposal': ProposalSerializer(proposal).data
        }, status=status.HTTP_200_OK)


class IsMessageParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.sender == request.user or obj.recipient == request.user
        return obj.sender == request.user


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsMessageParticipant()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(Q(sender=user) | Q(recipient=user))

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Users can see contracts where they are freelancer or client
        return Contract.objects.filter(Q(freelancer=user) | Q(client=user))

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        contract = self.get_object()
        
        # Verify that the requester is the freelancer or client
        if contract.freelancer != request.user and contract.client != request.user:
            return Response(
                {'error': 'Only contract participants can mark as complete'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if contract.status != Contract.STATUS_ACTIVE:
            return Response(
                {'error': f'Can only complete active contracts. Current status: {contract.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contract.status = Contract.STATUS_COMPLETED
        contract.is_completed = True
        contract.completed_at = timezone.now()
        contract.save()

        return Response({
            'message': 'Contract marked as completed',
            'contract': ContractSerializer(contract).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, pk=None):
        contract = self.get_object()
        
        # Only client can cancel
        if contract.client != request.user:
            return Response(
                {'error': 'Only the client can cancel contracts'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if contract.status != Contract.STATUS_ACTIVE:
            return Response(
                {'error': f'Can only cancel active contracts. Current status: {contract.status}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        contract.status = Contract.STATUS_CANCELLED
        contract.save()

        return Response({
            'message': 'Contract cancelled successfully',
            'contract': ContractSerializer(contract).data
        }, status=status.HTTP_200_OK)
