from django.db.models import Q
from django.contrib.auth import authenticate
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Profile, JobOffer, Proposal, Message
from .serializers import UserSerializer, LoginSerializer, JobOfferSerializer, ProposalSerializer, MessageSerializer


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
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsClient()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsClient(), IsOwnerOrReadOnly()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = JobOffer.objects.all()
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
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        profile = getattr(user, 'profile', None)
        if profile is None:
            profile, _ = Profile.objects.get_or_create(user=user)
        if profile.role == Profile.ROLE_FREELANCER:
            return Proposal.objects.filter(freelance=user)
        return Proposal.objects.filter(job_offer__client=user)

    def perform_create(self, serializer):
        serializer.save(freelance=self.request.user)


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
