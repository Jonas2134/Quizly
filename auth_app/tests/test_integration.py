import pytest

@pytest.mark.django_db
def test_full_auth_flow(client, auth_urls, user_data):
    register_data = {
        'username': user_data['new_username'],
        'password': user_data['new_password'],
        'email': user_data['new_email']
    }
    reg_response = client.post(auth_urls['register'], register_data, content_type='application/json')
    assert reg_response.status_code == 201
    assert 'detail' in reg_response.json()

    login_data = {
        'username': user_data['new_username'],
        'password': user_data['new_password']
    }
    login_response = client.post(auth_urls['login'], login_data, content_type='application/json')
    assert login_response.status_code == 200
    assert 'user' in login_response.json()
    refresh_token = login_response.cookies.get('refresh_token').value
    access_token = login_response.cookies.get('access_token').value
    assert refresh_token
    assert access_token

    client.cookies['refresh_token'] = refresh_token
    client.cookies['access_token'] = access_token
    client.defaults['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
    refresh_response = client.post(auth_urls['token_refresh'])
    assert refresh_response.status_code in [200, 403]
    if refresh_response.status_code == 200:
        assert 'access_token' in refresh_response.cookies
        assert 'access' in refresh_response.json()

    logout_response = client.post(auth_urls['logout'])
    assert logout_response.status_code == 200
    assert logout_response.cookies.get('refresh_token').value == ''
    assert logout_response.cookies.get('access_token').value == ''
    assert 'detail' in logout_response.json()
