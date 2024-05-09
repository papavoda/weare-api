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


### TODO https://stackoverflow.com/questions/55550089/django-rest-framework-using-session-and-token-auth?rq=3
@api_view(['GET'])
def protected_media(request, path, ):
    print('****** in protected USER *********', request.user)
    print('****** in protected USER.is_active *********', request.user.is_active)
    print('****** Auth *********', request.META)
    print('******* path *********', path)
    if request.user.is_active:
        response = HttpResponse(status=200)
        response["Content-Type"] = ''
        response['X-Accel-Redirect'] = '/protected-media/' + quote(path)
        return response
    else:
        return HttpResponse(status=400)


class ProtectedMedia(APIView):
    # authentication_classes = [JWTAuthentication]
    authentication_classes = [SessionAuthentication]
    def get(self, request, path, ):
        print('****** in protected USER *********', request.user)
        print('****** in protected USER.is_active *********', request.user.is_active)
        print('****** Auth *********', request.META)
        print('******* path *********', path)
        if request.user.is_active:
            response = HttpResponse(status=200)
            response["Content-Type"] = ''
            response['X-Accel-Redirect'] = '/protected-media/' + quote(path)
            return response
        else:
            return HttpResponse(status=400)
