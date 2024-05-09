from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from config import settings
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView, )
from rest_framework_simplejwt.views import TokenVerifyView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from blog.views import protected_media, ProtectedMedia

urlpatterns = [
    # re_path(r'^media/(?P<path>.*)', protected_media, name="protected_media"),
    # protected media files
    re_path(r'^media/(?P<path>.*)', ProtectedMedia.as_view(), name="pro_media"),

    # jwt signup, login
    path('api/v1/users/', include('accounts.urls')),
    # admin
    path('guliguli/', admin.site.urls),

    path('api/v1/', include('api.urls')),

    # session authentication
    path('api/v1/seauth/', include('seauth.urls')),

    # Simple JWT
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    #path('', include('blog.urls')),

    # drf-spectaculator
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Optional UI:
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# FOR debug_toolbar
# if settings.DEBUG:
#     import debug_toolbar
#
#     urlpatterns = [
#                       path('__debug__/', include(debug_toolbar.urls)),
#                   ] + urlpatterns
