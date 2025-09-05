from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(generics.CreateAPIView):
    """
    API view for user registration.
    Allows any user (authenticated or not) to access this endpoint.
    Uses the RegisterSerializer to validate and create a new user.

    Attributes:
        serializer_class (RegisterSerializer): The serializer class to use for this view.
        permission_classes (list): The permission classes to apply to this view.
    """
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user registration.

        1. Validate the incoming data using the serializer.
        2. If valid, save the new user and return a success message with HTTP 201 status.
        3. If invalid, return the serializer errors with HTTP 400 status
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            message = {"detail": "User created successfully!"}
            return Response(message, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    API view for user login.
    Allows any user (authenticated or not) to access this endpoint.
    Uses the LoginSerializer to validate and authenticate the user.

    Attributes:
        serializer_class (LoginSerializer): The serializer class to use for this view.
        permission_classes (list): The permission classes to apply to this view.
    """
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for user login.

        1. Validate the incoming data using the serializer.
        2. If valid, return the access and refresh tokens in HttpOnly cookies with HTTP 200 status.
        3. If invalid, return the serializer errors with HTTP 401 status.
        """
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            refresh = data.get('refresh')
            access = data.get('access')
            user = data.get('user')
            response = Response({"detail": "Login successfully!", "user": user}, status=status.HTTP_200_OK)
            response.set_cookie(
                key='refresh_token',
                value=refresh,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
            response.set_cookie(
                key='access_token',
                value=access,
                httponly=True,
                secure=True,
                samesite='Lax'
            )
        return response


class LogoutView(APIView):
    """
    API view for user logout.
    Requires the user to be authenticated to access this endpoint.
    Invalidates the refresh token and deletes the access and refresh tokens from cookies.

    Attributes:
        permission_classes (list): The permission classes to apply to this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests for user logout.

        1. Retrieve the refresh token from the HttpOnly cookie.
        2. If the token is found, blacklist it to invalidate it.
        3. Delete the access and refresh tokens from cookies.
        4. Return a success message with HTTP 200 status.
        5. If the token is not found or invalid, return an error message with HTTP 400 status.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({"detail": "Refresh token not found."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Token invalid"}, status=status.HTTP_400_BAD_REQUEST)

        response = Response({"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."}, status=status.HTTP_200_OK)
        response.delete_cookie('refresh_token')
        response.delete_cookie('access_token')
        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    API view for refreshing JWT access tokens using HttpOnly cookies.
    Allows authenticated users to refresh their access tokens.
    Retrieves the refresh token from an HttpOnly cookie and returns a new access token in an HttpOnly cookie.
    Attributes:
        permission_classes (list): The permission classes to apply to this view.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests for refreshing the access token.

        1. Retrieve the refresh token from the HttpOnly cookie.
        2. If the token is found, validate it and generate a new access token.
        3. Return the new access token in an HttpOnly cookie with HTTP 200 status.
        4. If the token is not found or invalid, return an error message with HTTP 401 status.
        """
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token is None:
            return Response({"detail": "Refresh token not found."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(data={"refresh":refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_401_UNAUTHORIZED)
        access_token = serializer.validated_data.get("access")
        response = Response({"access": "Access Token refreshed successfully."}, status=status.HTTP_200_OK)
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response
