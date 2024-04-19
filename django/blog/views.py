from urllib.parse import quote
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated





# @api_view(['GET'])
def protected_media(request, path, ):
    print('****** USER *********', request.user)
    print('****** USER.is_active *********', request.user.is_active)
    # print('****** Auth *********', request.META)

    if request.user:
        response = HttpResponse(status=200)
        response["Content-Type"] = ''
        response['X-Accel-Redirect'] = '/protected-media/' + quote(path)
        return response
    else:
        return HttpResponse(status=400)
