from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, make_response
)
from flask_login import current_user
from werkzeug.exceptions import abort

from blog.auth import login_required
from blog.models import Post, User
from blog.db import db

bp = Blueprint('posts', __name__)

def get_post(id, check_author=True):
    post = Post.query.filter_by(id=id).first()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and (current_user is None or post.author_id != current_user.id):
        abort(403)

    return post

@bp.route('/')
def index():
    posts = Post.query.all()
    return render_template('blog/index.html', posts=posts)

@bp.route('/<int:id>')
def detail(id):
    post = get_post(id, check_author=False)
    return render_template('blog/detail.html', post=post, like_count=len(post.like), isLiked=(current_user in post.like))

@bp.post('/<int:id>/like')
def like_article(id):
    if not current_user.is_authenticated:
        abort(403)
    else:
        post = get_post(id, check_author=False)
        if User.query.get(current_user.id) not in post.like:
            post.like.append(current_user)
        else:
            abort(400)
        db.session.commit()
        return str(len(post.like))

@bp.post('/<int:id>/dislike')
def dislike_article(id):
    if not current_user.is_authenticated:
        abort(403)
    else:
        post = get_post(id, check_author=False)
        if User.query.get(current_user.id) in post.like:
            post.like.remove(current_user)
        else:
            abort(400)
        db.session.commit()
        return str(len(post.like))


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            data = Post(title=title, body=body, author_id=current_user.id)
            db.session.add(data)
            db.session.commit()
            return redirect(url_for('posts.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            post = Post.query.filter_by(id=id).first()
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for('posts.index'))
    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('posts.index'))