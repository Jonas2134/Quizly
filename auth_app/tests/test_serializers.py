import pytest
from django.contrib.auth import get_user_model
from auth_app.api.serializers import RegisterSerializer, LoginSerializer

User = get_user_model()

@pytest.mark.django_db
def test_register_serializer_success(user_data):
    data = {'username': user_data['new_username'], 'email': user_data['new_email'], 'password': user_data['new_password']}
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert user.username == user_data['new_username']
    assert user.email == user_data['new_email']
    assert user.check_password(user_data['new_password'])

@pytest.mark.django_db
def test_register_serializer_duplicate_username(user_data):
    User.objects.create_user(username=user_data['username'], email='unique@example.com', password='pw')
    data = {'username': user_data['username'], 'email': 'unique2@example.com', 'password': 'pw'}
    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid()
    assert 'username' in serializer.errors

@pytest.mark.django_db
def test_register_serializer_duplicate_email(user_data):
    User.objects.create_user(username='uniqueuser', email=user_data['email'], password='pw')
    data = {'username': 'otheruser', 'email': user_data['email'], 'password': 'pw'}
    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid()
    assert 'email' in serializer.errors

@pytest.mark.django_db
def test_login_serializer_success(test_user, user_data):
    data = {'username': user_data['username'], 'password': user_data['password']}
    serializer = LoginSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    result = serializer.validated_data
    assert 'access' in serializer.validated_data
    assert 'refresh' in serializer.validated_data
    assert 'user' in serializer.validated_data
    assert result['user']['username'] == user_data['username']

@pytest.mark.django_db
def test_login_serializer_user_not_exist(user_data):
    data = {'username': 'nouser', 'password': 'pw'}
    serializer = LoginSerializer(data=data)
    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors or '__all__' in serializer.errors

@pytest.mark.django_db
def test_login_serializer_wrong_password(test_user, user_data):
    data = {'username': user_data['username'], 'password': user_data['wrong_password']}
    serializer = LoginSerializer(data=data)
    assert not serializer.is_valid()
    assert 'non_field_errors' in serializer.errors or '__all__' in serializer.errors