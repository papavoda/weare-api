from django.urls import path

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import api
from .api import MeAPI
from .views import PasswordResetView, PasswordResetConfirmView, activateemail

urlpatterns = [
    path('me/', MeAPI.as_view(), name='me'),
    path('signup/', api.signup, name='signup'),
    path('gallery-type/', api.toggle_simple_gallery, name='toggle_simple_gallery'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('activateemail/', activateemail, name='activateemail'),
]