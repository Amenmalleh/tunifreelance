from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register('joboffers', views.JobOfferViewSet, basename='joboffer')
router.register('proposals', views.ProposalViewSet, basename='proposal')
router.register('messages', views.MessageViewSet, basename='message')
router.register('contracts', views.ContractViewSet, basename='contract')
router.register('notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard/stats/', views.DashboardStatsView.as_view(), name='dashboard-stats'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('users/search/', views.UserSearchView.as_view(), name='user-search'),
    path('', include(router.urls)),
]
