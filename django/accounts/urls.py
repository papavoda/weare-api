from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .api import MeAPI, ToggleSimpleGallery, SignUp, PasswordResetView, PasswordResetConfirmView, ActivateEmailAPIView


urlpatterns = [
    path('me/', MeAPI.as_view(), name='me'),
    path('signup/', SignUp.as_view(), name='signup'),
    path('gallery-type/', ToggleSimpleGallery.as_view(), name='toggle_simple_gallery'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activateemail/', ActivateEmailAPIView.as_view(), name='activateemail'),
]