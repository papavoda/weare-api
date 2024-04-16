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
from rest_framework.generics import GenericAPIView

from .forms import SignupForm
from .models import CustomUser
from .serializers import CustomUserSerializer, UserSerializer, PasswordResetSerializer, PasswordResetConfirmSerializer


class MeAPI(APIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = CustomUserSerializer
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        user = request.user  # Assuming user is authenticated
        serializer = self.serializer_class(user, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignUp(GenericAPIView):
    authentication_classes =[]
    permission_classes = []
    serializer_class = UserSerializer

    def post(self, request):
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

class ToggleSimpleGallery(GenericAPIView):
    permission_classes = [IsAuthenticated, ]
    serializer_class = UserSerializer
    def post(self, request):
        user = request.user
        is_simple_gallery = request.GET.get('is-simple-gallery', '')
        if is_simple_gallery == 'true':
            user.is_simple_gallery = True
        elif is_simple_gallery == 'false':
            user.is_simple_gallery = False
        user.save()

        return JsonResponse({'isSimpleGallery': user.is_simple_gallery})

class EmailVerificationView(APIView):
    # serializer_class = ''
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


class PasswordResetView(GenericAPIView):
    permission_classes = []
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data['email']

            user = CustomUser.objects.filter(email=email).first()
            if user:
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                token = default_token_generator.make_token(user)
                # reset_link = f"http://localhost:8008/api/password_reset/confirm/?uid={uid}&token={token}"
                reset_link = f"http://localhost:5173/password-reset/confirm/{uid}/{token}"

                # email_body = render_to_string({'reset_link': reset_link})
                send_mail('Password Reset link', reset_link, 'from@example.com', [email])
            return Response({'detail': 'Password reset email sent'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(GenericAPIView):
    permission_classes = []
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
            user = CustomUser.objects.filter(pk=uid).first()
            if user and default_token_generator.check_token(user, serializer.validated_data['token']):
                user.set_password(serializer.validated_data['password2'])
                user.save()
                return Response({'detail': 'Password reset successfully'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid or expired reset link'}, status=status.HTTP_400_BAD_REQUEST)



class ActivateEmailAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    serializer_class = UserSerializer
    def post(self, request):
        # Extract data from the POST request
        uid = request.data['uid']
        email = request.data['email']

        if email and uid:
            user = CustomUser.objects.get(id=uid, email=email)
            user.is_active = True
            user.save()

            return Response('The user is now activated. You can go ahead and log in!')
        else:
            return Response('The parameters is not valid!', status=status.HTTP_400_BAD_REQUEST)