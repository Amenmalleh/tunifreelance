from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('joboffers', views.JobOfferViewSet, basename='joboffer')
router.register('proposals', views.ProposalViewSet, basename='proposal')
router.register('messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('', include(router.urls)),
]
