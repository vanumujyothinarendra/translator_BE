from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.models import User


class RegisterSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "confirm_password"]

    def validate(self, data):

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        return data

    def create(self, validated_data):

        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )

        return user


class LoginSerializer(serializers.Serializer):

    username_or_email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):

        username_or_email = data.get("username_or_email")
        password = data.get("password")

        user = None

        # Check if input is email
        if "@" in username_or_email:
            try:
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        else:
            user = authenticate(username=username_or_email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid username/email or password")

        data["user"] = user
        return data