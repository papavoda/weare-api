from django.contrib.auth.forms import PasswordChangeForm
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .models import CustomUser
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from .serializers import PasswordResetSerializer, PasswordResetConfirmSerializer, UserSerializer, CustomUserSerializer





@api_view(['POST'])

def editpassword(request):
    user = request.user

    form = PasswordChangeForm(data=request.POST, user=user)

    if form.is_valid():
        form.save()

        return JsonResponse({'message': 'success'})
    else:
        return JsonResponse({'message': form.errors.as_json()}, safe=False)

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



@api_view(['POST'])
@authentication_classes([])
@permission_classes([])
def activateemail(request):
    # Extract data from the POST request
    uid = request.data['uid']
    email = request.data['email']

    if email and uid:
        user = CustomUser.objects.get(id=uid, email=email)
        user.is_active = True
        user.save()

        return Response('The user is now activated. You can go ahead and log in!')
    else:
        return Response('The parameters is not valid!')

