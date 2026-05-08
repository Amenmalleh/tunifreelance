from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register('joboffers', views.JobOfferViewSet, basename='joboffer')
router.register('proposals', views.ProposalViewSet, basename='proposal')
router.register('messages', views.MessageViewSet, basename='message')
router.register('contracts', views.ContractViewSet, basename='contract')

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/client/stats/', views.ClientDashboardStatsView.as_view(), name='client-dashboard-stats'),
    path('dashboard/freelancer/stats/', views.FreelancerDashboardStatsView.as_view(), name='freelancer-dashboard-stats'),
    path('', include(router.urls)),
]
