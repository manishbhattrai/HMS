from rest_framework.routers import DefaultRouter
from .views import UserLoginView, UserLogoutView, UserRegistrationView, UserProfileView,ChangePasswordView
from django.urls import path, include


router = DefaultRouter()


router.register(r'profile', UserProfileView, basename='userprofile')


urlpatterns = [

    path('',include(router.urls)),
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/logout/',UserLogoutView.as_view(), name='logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password')

]