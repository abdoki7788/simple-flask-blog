from flask_login import current_user
import pytest
from blog.db import db
from blog.models import Post, User


def test_index(client, auth):
    response = client.get('/')
    assert b"Log In" in response.data
    assert b"Register" in response.data

    auth.login()
    response = client.get('/')
    assert b'Log Out' in response.data
    assert b'test title' in response.data
    assert b'by test on 2018-01-01' in response.data
    assert b'test\nbody' in response.data
    assert b'href="/1/update"' in response.data

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
    '/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.status == "401 UNAUTHORIZED"

def test_author_required(app, client, auth):
    with app.app_context():
        post = Post.query.filter_by(id=1).first()
        post.author_id = 2
        db.session.commit()

    auth.login()
    assert client.post('/1/update').status_code == 403
    assert client.post('/1/delete').status_code == 403
    assert b'href="/1/update"' not in client.get('/').data

@pytest.mark.parametrize('path', (
    '/2/update',
    '/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404

def test_create(client, auth, app):
    auth.login()
    assert client.get('/create').status_code == 200
    client.post('/create', data={'title': 'created', 'body': '...'})

    with app.app_context():
        count = db.session.query(Post).count()
        assert count == 2

def test_update(client, auth, app):
    auth.login()
    assert client.get('/1/update').status_code == 200
    res = client.post('/1/update', data={'title': 'updated', 'body': 'this is the body'})
    print(res.data)


    with app.app_context():
        post = Post.query.filter_by(id=1).first()
        assert post.title == 'updated'

def test_detail(client, app):
    response = client.get('/1')
    assert response.status_code == 200

    with app.app_context():
        post = Post.query.filter_by(id=1).first()
        assert post.title in str(response.data)

@pytest.mark.parametrize('path', (
    '/create',
    '/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'title': '', 'body': ''})
    assert b'This field is required.' in response.data

def test_delete(client, auth, app):
    auth.login()
    response = client.post('/1/delete')
    assert response.headers["Location"] == "/"

    with app.app_context():
        post = Post.query.filter_by(id=1).first()
        assert post is None

def test_like(client, auth, app):
    response = client.post("/1/like")
    article = client.get("/1")
    assert response.status_code == 403
    assert article.status_code == 200
    assert b'<span id="likes_count">0</span>' in article.data
    auth.login()

    with client, app.app_context():
        response = client.post("/1/like")
        article = client.get("/1")
        post = Post.query.filter_by(id=1).first()
        assert User.query.filter_by(id=current_user.id).first() in post.like
        assert response.status_code == 200
        assert response.data == b"1"
        assert article.status_code == 200
        assert b'<span id="likes_count">1</span>' in article.data
        response = client.post("/1/like")
        assert response.status_code == 400

def test_dislike(client, auth, app):
    response = client.post("/1/dislike")
    article = client.get("/1")
    assert response.status_code == 403
    assert article.status_code == 200
    assert b'<span id="likes_count">0</span>' in article.data
    auth.login()

    with client, app.app_context():
        client.post("/1/like")
        response = client.post("/1/dislike")
        article = client.get("/1")
        post = Post.query.filter_by(id=1).first()
        assert User.query.get(current_user.id) not in post.like
        assert response.status_code == 200
        assert response.data == b"0"
        assert article.status_code == 200
        assert b'<span id="likes_count">0</span>' in article.data
        response = client.post("/1/dislike")
        assert response.status_code == 400