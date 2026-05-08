from django.db import transaction
from django.db.models import Q, Sum, Count
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, JobOffer, Proposal, Message, Contract, Notification
from .serializers import (
    UserSerializer, LoginSerializer, JobOfferSerializer,
    ProposalSerializer, MessageSerializer, ContractSerializer,
    NotificationSerializer
)


# ──────────────────────────────────────────────
#  Utility: create a notification
# ──────────────────────────────────────────────
def create_notification(user, notification_type, title, message='', link=''):
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )


# ──────────────────────────────────────────────
#  AUTH
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
#  DASHBOARD STATS
# ──────────────────────────────────────────────
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = getattr(user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=user)

        if profile.role == Profile.ROLE_FREELANCER:
            # Freelancer stats
            completed_contracts = Contract.objects.filter(
                freelancer=user, status=Contract.STATUS_COMPLETED
            )
            earnings = completed_contracts.aggregate(
                total=Sum('contract_price')
            )['total'] or 0

            active_proposals = Proposal.objects.filter(
                freelance=user,
                status=Proposal.STATUS_ACCEPTED,
                contract__isnull=True
            ).count()

            completed_jobs = completed_contracts.count()

            active_contracts = Contract.objects.filter(
                freelancer=user, status=Contract.STATUS_ACTIVE
            ).count()

            return Response({
                'role': 'freelancer',
                'earnings': float(earnings),
                'active_proposals': active_proposals,
                'completed_jobs': completed_jobs,
                'active_contracts': active_contracts,
            })
        else:
            # Client stats
            completed_contracts = Contract.objects.filter(
                client=user, status=Contract.STATUS_COMPLETED
            )
            spendings = completed_contracts.aggregate(
                total=Sum('contract_price')
            )['total'] or 0

            active_jobs = JobOffer.objects.filter(
                client=user, status=JobOffer.STATUS_OPEN
            ).count()

            total_applicants = Proposal.objects.filter(
                job_offer__client=user
            ).count()

            active_contracts = Contract.objects.filter(
                client=user, status=Contract.STATUS_ACTIVE
            ).count()

            return Response({
                'role': 'client',
                'spendings': float(spendings),
                'active_jobs': active_jobs,
                'total_applicants': total_applicants,
                'active_contracts': active_contracts,
            })


# ──────────────────────────────────────────────
#  USER PROFILE
# ──────────────────────────────────────────────
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserSearchView(APIView):
    """Search users by username to start a conversation."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if len(query) < 2:
            return Response([])

        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).exclude(id=request.user.id)[:10]

        data = [{
            'id': u.id,
            'username': u.username,
            'first_name': u.first_name,
            'last_name': u.last_name,
            'role': getattr(getattr(u, 'profile', None), 'role', 'freelancer')
        } for u in users]

        return Response(data)


# ──────────────────────────────────────────────
#  PERMISSIONS
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
#  JOB OFFERS (with search & filter)
# ──────────────────────────────────────────────
class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsClient()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsClient(), IsOwnerOrReadOnly()]
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = JobOffer.objects.all()
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

        # ── Search & Filter ──
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )

        category = self.request.query_params.get('category', '')
        if category:
            queryset = queryset.filter(category__icontains=category)

        min_budget = self.request.query_params.get('min_budget')
        if min_budget:
            queryset = queryset.filter(budget__gte=min_budget)

        max_budget = self.request.query_params.get('max_budget')
        if max_budget:
            queryset = queryset.filter(budget__lte=max_budget)

        location = self.request.query_params.get('location', '')
        if location:
            queryset = queryset.filter(location__icontains=location)

        sort = self.request.query_params.get('sort', '-created_at')
        if sort in ['created_at', '-created_at', 'budget', '-budget', 'deadline', '-deadline']:
            queryset = queryset.order_by(sort)

        return queryset

    def perform_create(self, serializer):
        serializer.save(client=self.request.user)


# ──────────────────────────────────────────────
#  PROPOSALS
# ──────────────────────────────────────────────
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
        if self.action == 'approve':
            return [permissions.IsAuthenticated(), IsFreelance()]
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
        proposal = serializer.save(freelance=self.request.user)
        # Notify the client
        create_notification(
            user=proposal.job_offer.client,
            notification_type='proposal_received',
            title=f'New proposal from {self.request.user.username}',
            message=f'For the project "{proposal.job_offer.title}" — {proposal.proposed_price} DT',
            link=f'/proposals'
        )

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

            proposal.status = Proposal.STATUS_ACCEPTED
            proposal.save(update_fields=['status'])

            # Notify the freelancer
            create_notification(
                user=proposal.freelance,
                notification_type='proposal_accepted',
                title='Proposal accepted!',
                message=f'Your proposal for "{proposal.job_offer.title}" has been accepted by the client. Please approve it to create a contract.',
                link='/dashboard'
            )

        return Response({
            'message': 'Proposal accepted successfully. Waiting for freelancer approval.',
            'proposal': ProposalSerializer(proposal).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        with transaction.atomic():
            proposal = Proposal.objects.select_for_update().select_related('job_offer', 'freelance').get(pk=pk)

            if proposal.freelance != request.user:
                return Response(
                    {'error': 'Only the freelancer can approve accepted proposals'},
                    status=status.HTTP_403_FORBIDDEN
                )

            if proposal.status != Proposal.STATUS_ACCEPTED:
                return Response(
                    {'error': f'Can only approve accepted proposals. Current status: {proposal.status}'},
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
                client=proposal.job_offer.client,
                contract_price=proposal.proposed_price,
                contract_deadline=proposal.proposed_deadline or proposal.job_offer.deadline,
                amount_locked=proposal.proposed_price
            )

            # Close other pending proposals for this job
            Proposal.objects.filter(
                job_offer=proposal.job_offer,
                status=Proposal.STATUS_PENDING
            ).exclude(pk=proposal.pk).update(status=Proposal.STATUS_REJECTED)

            proposal.job_offer.status = JobOffer.STATUS_CLOSED
            proposal.job_offer.save(update_fields=['status'])

            # Notify the client
            create_notification(
                user=proposal.job_offer.client,
                notification_type='contract_created',
                title='Contract created',
                message=f'{proposal.freelance.username} approved the proposal and the contract is now active.',
                link='/dashboard'
            )

        return Response({
            'message': 'Proposal approved and contract created successfully',
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

        # Notify the freelancer
        create_notification(
            user=proposal.freelance,
            notification_type='proposal_rejected',
            title='Proposal rejected',
            message=f'Your proposal for "{proposal.job_offer.title}" has been rejected.',
            link='/dashboard'
        )

        return Response({
            'message': 'Proposal rejected successfully',
            'proposal': ProposalSerializer(proposal).data
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
#  MESSAGES
# ──────────────────────────────────────────────
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
        queryset = Message.objects.filter(Q(sender=user) | Q(recipient=user))

        # Filter by conversation partner
        partner_id = self.request.query_params.get('partner')
        if partner_id:
            queryset = queryset.filter(
                Q(sender_id=partner_id) | Q(recipient_id=partner_id)
            )

        return queryset

    def perform_create(self, serializer):
        msg = serializer.save(sender=self.request.user)
        # Notify recipient
        create_notification(
            user=msg.recipient,
            notification_type='message_received',
            title=f'New message from {self.request.user.username}',
            message=msg.content[:100],
            link='/messages'
        )

    @action(detail=False, methods=['post'], url_path='mark-read')
    def mark_conversation_read(self, request):
        """Mark all messages from a partner as read."""
        partner_id = request.data.get('partner_id')
        if not partner_id:
            return Response({'error': 'partner_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        updated = Message.objects.filter(
            sender_id=partner_id,
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({'marked_read': updated})


# ──────────────────────────────────────────────
#  CONTRACTS
# ──────────────────────────────────────────────
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

        # Notify both parties
        other_user = contract.client if request.user == contract.freelancer else contract.freelancer
        create_notification(
            user=other_user,
            notification_type='contract_completed',
            title='Contract completed',
            message=f'The contract for "{contract.job_offer.title}" has been marked as completed.',
            link='/dashboard'
        )

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

        # Notify the freelancer
        create_notification(
            user=contract.freelancer,
            notification_type='contract_cancelled',
            title='Contract cancelled',
            message=f'The contract for "{contract.job_offer.title}" has been cancelled by the client.',
            link='/dashboard'
        )

        return Response({
            'message': 'Contract cancelled successfully',
            'contract': ContractSerializer(contract).data
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
#  NOTIFICATIONS
# ──────────────────────────────────────────────
class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'count': count})

    @action(detail=True, methods=['post'], url_path='mark-read')
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        updated = Notification.objects.filter(
            user=request.user, is_read=False
        ).update(is_read=True)
        return Response({'marked_read': updated})
