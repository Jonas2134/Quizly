import pytest
from django.contrib.auth.models import User
from django.test import Client

@pytest.fixture
def test_user(db):
    user = User.objects.create_user(username='testuser', password='testpass123')
    return user

@pytest.fixture
def client():
    return Client()

@pytest.fixture
def auth_urls():
    return {
        'register': '/api/register/',
        'login': '/api/login/',
        'logout': '/api/logout/',
        'token_refresh': '/api/token/refresh/'
    }

@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'password': 'testpass123',
        'email': 'testuser@example.com',
        'wrong_password': 'falsch',
        'new_username': 'newuser',
        'new_password': 'neuespasswort123',
        'new_email': 'newuser@example.com'
    }