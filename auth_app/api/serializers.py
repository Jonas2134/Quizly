from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value
    
    def save(self, **kwargs):
        pw = self.validated_data.pop('password')
        user = User(**self.validated_data)
        user.set_password(pw)
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
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
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this username does not exist.")
    
    def _check_password(self, user, password) -> None:
        if not user.check_password(password):
            raise serializers.ValidationError("Incorrect password.")
