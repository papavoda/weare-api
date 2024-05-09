
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie

from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import LoginSerializer, SignupSerializer


class WhoAmI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
            return JsonResponse({"message": f"Hello, {request.user}"}, status=200)
        else:
            return JsonResponse({"message": "Some error!"}, status=401)


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None and user.is_active is True:
                login(request, user)
                return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated, ]

    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"}, status=status.HTTP_200_OK, )


@login_required
@ensure_csrf_cookie
def session_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({'isAuthenticated': False})
    print(request.user.id)
    return JsonResponse({'isAuthenticated': True})
