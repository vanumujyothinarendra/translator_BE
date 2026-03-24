from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from langdetect import detect
from googletrans import Translator

from .models import Message
from .serializers import RegisterSerializer, LoginSerializer


translator = Translator()
User = get_user_model()


# -------------------------------
# Register
# -------------------------------
class RegisterView(APIView):

    def post(self, request):

        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                {"message": "User created successfully"},
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Login
# -------------------------------
class LoginView(APIView):

    def post(self, request):

        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():

            user = serializer.validated_data["user"]

            refresh = RefreshToken.for_user(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------
# Translate
# -------------------------------
class TranslateView(APIView):
    
    def post(self, request):

        text = request.data.get("text")
        target_language = request.data.get("target_language")

        if not text or not target_language:
            return Response(
                {"error": "Text and target_language are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            detected_language = detect(text)

            translated = translator.translate(text, dest=target_language)

            # Save only if user is authenticated
            if request.user.is_authenticated:
                Message.objects.create(
                    user=request.user,
                    original_text=text,
                    translated_text=translated.text,
                    language=target_language
                )

            return Response({
                "original_text": text,
                "detected_language": detected_language,
                "translated_text": translated.text,
                "target_language": target_language
            })

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# -------------------------------
# Forgot Password
# -------------------------------
class ForgotPasswordView(APIView):

    def post(self, request):

        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)

        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"http://localhost:8080/reset-password?user_id={user.id}&token={token}"

        send_mail(
            "Password Reset",
            f"Click the link to reset your password:\n\n{reset_link}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False
        )

        return Response({"message": "Reset email sent"})


# -------------------------------
# Reset Password
# -------------------------------
class ResetPasswordView(APIView):

    def post(self, request):

        user_id = request.data.get("user_id")
        token = request.data.get("token")
        password = request.data.get("password")

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid user"}, status=404)

        if PasswordResetTokenGenerator().check_token(user, token):

            user.set_password(password)
            user.save()

            return Response({"message": "Password reset successful"})

        return Response({"error": "Invalid token"}, status=400)