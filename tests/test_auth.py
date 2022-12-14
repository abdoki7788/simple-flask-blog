import pytest
from flask import session
from blog.db import db
from blog.models import User
from flask_login import current_user


def test_register(client, app):
    assert client.get('/auth/register').status_code == 200
    response = client.post(
        '/auth/register', data={'username': 'a', 'password': 'a', 'repeat_password': 'a'}
    )
    assert response.headers['Location'] == '/auth/login'
    with app.app_context():
        assert User.query.filter_by(username='a').first() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', b'This field is required.'),
    ('a', '', b'This field is required.'),
    ('test', 'test', b'already registered.'),
))
def test_register_validate_input(client, username, password, message):
    response = client.post(
        '/auth/register',
        data={'username': username, 'password': password, 'repeat_password': password}
    )
    print(response.data)
    assert message in response.data

def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        print(session)
        assert session['_user_id'] == '1'
        assert current_user.username == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
