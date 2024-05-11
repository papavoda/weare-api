from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.http.response import HttpResponseForbidden
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication



def protected_media(request, path):
#    print('****** in protected USER *********', request.user)
    if request.user.is_authenticated:
        response = HttpResponse(status=200)
        response["Content-Type"] = ''
        response['X-Accel-Redirect'] = '/protected-media/' + quote(path)
        return response
    else:
        return HttpResponse(status=400)



