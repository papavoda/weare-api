# api/urls.py

from django.urls import path
from .views import LoginView, LogoutView,  SignupView, WhoAmI, session_view

urlpatterns = [
    # path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', WhoAmI.as_view(), name='whoami'),
    path('session/', session_view, name='api-session'),
]

