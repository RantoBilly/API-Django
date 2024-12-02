from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from django.contrib.auth import authenticate
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from .token import account_activation_token


class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # generating activation link
            activation_link = f"http://{request.get_host()}/api/user/activate/{user.id}"
            send_mail(
                "Account activation",
                f"Click the link to activate your account : {activation_link}",
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            return Response({
                "message": "User registered. Please check your email for activation link."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# handling account activation
class ActivateAccountView(APIView):
    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save()
        return Response({"message": "Account activated successfully !"}, status=status.HTTP_200_OK)


class LoginView(ObtainAuthToken):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({
                "status": False,
                "message": "wrong password or wrong email"
            })

        user.check_password(password)

        if not user.check_password(password):
            return Response({
                "status": False,
                "message": "wrong password or wrong email"
            })

        if not user.is_active:
            return Response({"error": "Account is not activated. Please activate your account."}, status=403)

        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)

        return Response({
            "status": True,
            "message": "Login success !",
            "data": {
                "accessToken": str(access_token),
                "refreshToken": str(refresh_token)
            },
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refreshToken")
            if not refresh_token:
                return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist() # blacklist the refresh token

            return Response({"message": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token or token already blacklisted"}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "user with this email does not exist"}, status=404)

        # Reset Link
        token = account_activation_token.make_token(user)
        reset_link = f"http://{request.get_host()}/api/user/reset-password/{user.id}/{token}"

        # send email
        send_mail(
            subject="Password Reset Request",
            message=f"Clink the link to reset your password: {reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        return Response({"message": "Password reset link sent to your email"}, status=200)


class PasswordResetConfirmView(APIView):
    def post(self, request, user_id, token):
        password = request.data.get('password')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user."}, status=404)

        # verify token
        if not account_activation_token.check_token(user, token):
            return Response({"error": "Invalid  or expired token"}, status=404)

        # update password
        user.set_password(password)
        user.save()

        return Response({"message": "Password has been reset successfully"}, status=200)



