from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path


from config import settings
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView, )
from rest_framework_simplejwt.views import TokenVerifyView



urlpatterns = [
    path('api/', include('accounts.urls')),
    path('guliguli/', admin.site.urls),

    path('api/v1/', include('api.urls')),

    # Simple JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    # path('', include('blog.urls')),

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
