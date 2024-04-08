from django.http import HttpResponse
from django.shortcuts import render

from .models import CustomUser


def activateemail(request):
    email = request.GET.get('email', '')
    id = request.GET.get('id', '')

    if email and id:
        user = CustomUser.objects.get(id=id, email=email)
        user.is_active = True
        user.save()

        return HttpResponse('The user is now activated. You can go ahead and log in!')
    else:
        return HttpResponse('The parameters is not valid!')


