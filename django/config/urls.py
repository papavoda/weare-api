from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


from config import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, )
from rest_framework_simplejwt.views import TokenVerifyView

from accounts.views import activateemail

urlpatterns = [
    path('api/', include('accounts.urls')),
    path('guliguli/', admin.site.urls),

    path('api/v1/', include('api.urls')),
    # path("api-auth/", include("rest_framework.urls")), # add auth
    path("api/v1/dj-rest-auth/", include("dj_rest_auth.urls")),
    path("api/v1/dj-rest-auth/registration/",
         include("dj_rest_auth.registration.urls")),  # add registration

    # Simple JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # path('', include('blog.urls')),
    path('activateemail/', activateemail, name='activateemail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# FOR debug_toolbar
if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
