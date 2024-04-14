from django.core.mail import send_mail
from django.http import JsonResponse
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from datetime import timedelta
from django.utils.encoding import force_str
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import PostSerializer
from blog.models import Post
from config import settings
from .forms import SignupForm
from .models import CustomUser
from .serializers import CustomUserSerializer


#  Return user data
# @api_view(['GET'])
# def me(request):
#     user = request.user
#     serializer = CustomUserSerializer(user)
#     return Response(serializer.data, status=status.HTTP_200_OK)

class MeAPI(APIView):
    permission_classes = [IsAuthenticated, ]
    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user  # Assuming user is authenticated
        serializer = CustomUserSerializer(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#  Register
@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def signup(request):
    data = request.data
    message = 'success'

    form = SignupForm({
        'email': data.get('email'),
        'name': data.get('name'),
        'password1': data.get('password1'),
        'password2': data.get('password2'),
    })
    # Check if the email already exists
    if CustomUser.objects.filter(email=data.get('email')).exists():
        return JsonResponse({'message': 'Email already exists'}, status=400)
    else:
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            # TODO Change to front url
            # url = f'{settings.WEBSITE_URL}/api/v1/users/activateemail/?email={user.email}&id={user.id}'
            url = f'http://localhost:5173/activateemail/{user.email}/{user.id}'

            send_mail(
                "Please verify your email",
                f"The url for activating your account is: {url}",
                "papavoda@gmail.com",
                [user.email],
                fail_silently=False,
            )
            return JsonResponse({'message': message}, status=201)
        else:
            message = form.errors.as_json()
            # print(message)
            return JsonResponse({'message': message}, status=400)


@api_view(['POST'])
def toggle_simple_gallery(request,):
    user = request.user
    isSimpleGallery = request.GET.get('is-simple-gallery', '')
    if isSimpleGallery == 'true':
        user.is_simple_gallery = True
    elif isSimpleGallery == 'false':
        user.is_simple_gallery = False
    user.save()

    return JsonResponse({'isSimpleGallery': user.is_simple_gallery})


class EmailVerificationView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            # Check if the verification link has expired
            if user.date_joined + timedelta(days=1) < timezone.now():
                return Response({'detail': 'Verification link has expired'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()
            return Response({'detail': 'Email verified successfully'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid verification link'}, status=status.HTTP_400_BAD_REQUEST)
