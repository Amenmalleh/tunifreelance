from django.db import transaction
from django.db.models import Avg, Q, Sum
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


class JobOfferPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 50

from .models import Profile, JobOffer, Proposal, Message, Contract, Rating
from .serializers import UserSerializer, LoginSerializer, JobOfferSerializer, ProposalSerializer, MessageSerializer, ContractSerializer, RatingSerializer


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
        if serializer.is_valid():
            user = authenticate(
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'user': UserSerializer(user).data,
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    pagination_class = JobOfferPagination

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
            return queryset.filter(status=JobOffer.STATUS_OPEN)
        profile = getattr(user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role == Profile.ROLE_FREELANCER:
            return queryset.filter(status=JobOffer.STATUS_OPEN)
        return queryset.filter(Q(status=JobOffer.STATUS_OPEN) | Q(client=user))

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
        base = Proposal.objects.select_related('job_offer', 'freelance', 'freelance__profile')
        if profile.role == Profile.ROLE_FREELANCER:
            return base.filter(freelance=user)
        return base.filter(job_offer__client=user)

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
        return Contract.objects.select_related(
            'proposal', 'proposal__freelance', 'proposal__job_offer',
            'job_offer', 'freelancer', 'client'
        ).filter(Q(freelancer=user) | Q(client=user))

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


class ClientDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        total_expenses = Contract.objects.filter(
            client=user,
            status=Contract.STATUS_COMPLETED
        ).aggregate(total=Sum('contract_price'))['total'] or 0

        active_jobs = JobOffer.objects.filter(
            client=user,
            status=JobOffer.STATUS_OPEN
        ).count()

        total_jobs = JobOffer.objects.filter(client=user).count()
        jobs_with_proposals = JobOffer.objects.filter(
            client=user,
            proposals__isnull=False
        ).distinct().count()
        hire_rate = round(jobs_with_proposals / total_jobs * 100, 1) if total_jobs > 0 else 0.0

        return Response({
            'total_expenses': float(total_expenses),
            'active_jobs': active_jobs,
            'hire_rate': hire_rate,
        })


class FreelancerDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        total_revenue = Contract.objects.filter(
            freelancer=user,
            status=Contract.STATUS_COMPLETED
        ).aggregate(total=Sum('contract_price'))['total'] or 0

        active_proposals_qs = Proposal.objects.filter(
            freelance=user,
            status=Proposal.STATUS_PENDING
        ).select_related('job_offer')

        active_proposals_list = [
            {
                'id': p.id,
                'job_title': p.job_offer.title,
                'proposed_price': float(p.proposed_price),
                'created_at': p.created_at.isoformat(),
            }
            for p in active_proposals_qs
        ]

        ratings_qs = Rating.objects.filter(freelancer=user)
        ratings_count = ratings_qs.count()
        avg = ratings_qs.aggregate(avg=Avg('score'))['avg']
        profile_score = round(avg, 1) if avg is not None else None

        return Response({
            'total_revenue': float(total_revenue),
            'active_proposals': len(active_proposals_list),
            'active_proposals_list': active_proposals_list,
            'profile_score': profile_score,
            'ratings_count': ratings_count,
        })
