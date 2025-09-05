from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Validates that the username and email are unique.
    Hashes the password before saving the user.

    Fields:
        email (str): The user's email address.
        username (str): The user's username.
        password (str): The user's password (write-only).
    """
    class Meta:
        """
        Meta class for RegisterSerializer.
        Specifies the model and fields to be used.

        Attributes:
            model (User): The user model.
            fields (tuple): The fields to be included in the serializer.
            extra_kwargs (dict): Additional keyword arguments for fields.
        """
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        """Validate the username field."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        """Validate the email field."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value
    
    def save(self, **kwargs):
        """
        Save the user instance.
        Hashes the password before saving the user.
        """
        pw = self.validated_data.pop('password')
        user = User(**self.validated_data)
        user.set_password(pw)
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Serializer for user login.
    Validates the username and password.
    Returns the data required for JWT authentication.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Validate the login credentials."""
        username = attrs.get('username')
        password = attrs.get('password')

        user = self._check_user_exist(username)
        self._check_password(user, password)

        attrs['username'] = user.username
        data = super().validate(attrs)
        data['user'] = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
        }
        return data

    def _check_user_exist(self, username):
        """Return user if exists, else raise ValidationError."""
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
    
    def _check_password(self, user, password) -> None:
        """Check if the provided password is correct."""
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
