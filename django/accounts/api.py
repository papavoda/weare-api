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
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import PostSerializer
from blog.models import Post
from config import settings
from .forms import SignupForm
from .models import CustomUser
from .serializers import CustomUserSerializer


#  Return user data
@api_view(['GET'])
def me(request):
    # posts = Post.objects.filter(author_id=request.user.id)
    # serializer = PostSerializer(posts, many=True)
    return JsonResponse({
        'id': request.user.id,
        'name': request.user.name,
        'email': request.user.email,
        'is_superuser': request.user.is_superuser,
        'isSimpleGallery': request.user.is_simple_gallery,
        # 'posts': serializer.data
    })


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

    if form.is_valid():
        user = form.save()
        user.is_active = False
        user.save()

        url = f'{settings.WEBSITE_URL}/activateemail/?email={user.email}&id={user.id}'

        send_mail(
            "Please verify your email",
            f"The url for activating your account is: {url}",
            "papavoda@gmail.com",
            [user.email],
            fail_silently=False,
        )

    else:
        message = form.errors.as_json()
        # print(message)
    return JsonResponse({'message': message})


@api_view(['POST'])
def toggle_simple_gallery(request, user_id):

    user = request.user
    isSimpleGallery = request.GET.get('is-simple-gallery', '')
    if isSimpleGallery == 'true':
        user.is_simple_gallery = True
    elif isSimpleGallery == 'false':
        user.is_simple_gallery = False
    user.save()

    return JsonResponse({'isSimpleGallery': user.is_simple_gallery })


# views.py

# Test from chatgpt
class UserRegistrationView(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Send verification email
            self.send_verification_email(request, user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_verification_email(self, request, user):
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        verification_url = reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
        verification_url = request.build_absolute_uri(verification_url)
        subject = 'Verify your email'
        message = f'Please click the link below to verify your email:\n{verification_url}'
        send_mail(subject, message, 'papavoda@gmail.com', [user.email])


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
