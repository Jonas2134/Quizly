import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_register_view(client, auth_urls, user_data):
    url = auth_urls['register']
    data = {'username': user_data['new_username'], 'password': user_data['new_password'], 'email': user_data['new_email']}
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 201
    assert 'detail' in response.json()


@pytest.mark.django_db
def test_login_view_success(client, test_user, auth_urls, user_data):
    url = auth_urls['login']
    data = {'username': user_data['username'], 'password': user_data['password']}
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 200
    assert 'detail' in response.json()
    assert 'user' in response.json()
    assert 'refresh_token' in response.cookies
    assert 'access_token' in response.cookies


@pytest.mark.django_db
def test_login_view_wrong_password(client, test_user, auth_urls, user_data):
    url = auth_urls['login']
    data = {'username': user_data['username'], 'password': user_data['wrong_password']}
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert 'detail' not in response.json() or 'user' not in response.json()


@pytest.mark.django_db
def test_logout_view(client, test_user, auth_urls, user_data):
    login_url = auth_urls['login']
    login_data = {'username': user_data['username'], 'password': user_data['password']}
    login_response = client.post(login_url, login_data, content_type='application/json')
    refresh_token = login_response.cookies.get('refresh_token').value
    access_token = login_response.cookies.get('access_token').value
    client.cookies['refresh_token'] = refresh_token
    client.cookies['access_token'] = access_token
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    logout_url = auth_urls['logout']
    response = client.post(logout_url)
    assert response.status_code == 200
    assert 'detail' in response.json()
    assert response.cookies.get('refresh_token').value == ''
    assert response.cookies.get('access_token').value == ''


@pytest.mark.django_db
def test_logout_view_no_token(client, auth_urls):
    url = auth_urls['logout']
    response = client.post(url)
    assert response.status_code == 401
    assert 'detail' not in response.json() or 'credentials' in response.json().get('detail', '').lower()


@pytest.mark.django_db
def test_token_refresh_view(client, test_user, auth_urls, user_data):
    login_url = auth_urls['login']
    login_data = {'username': user_data['username'], 'password': user_data['password']}
    login_response = client.post(login_url, login_data, content_type='application/json')
    refresh_token = login_response.cookies.get('refresh_token').value
    access_token = login_response.cookies.get('access_token').value
    client.cookies['refresh_token'] = refresh_token
    client.cookies['access_token'] = access_token
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    refresh_url = auth_urls['token_refresh']
    response = client.post(refresh_url)
    assert response.status_code in [200, 403]
    if response.status_code == 200:
        assert 'access_token' in response.cookies
        assert 'access' in response.json()


@pytest.mark.django_db
def test_token_refresh_view_no_token(client, auth_urls):
    url = auth_urls['token_refresh']
    response = client.post(url)
    assert response.status_code == 403
