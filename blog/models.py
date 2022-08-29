from datetime import datetime

from flask_login import UserMixin
from blog.db import db

associate_post_likes = db.Table(
    "post_likes",
    db.metadata,
    db.Column("post_id", db.ForeignKey("post.id"), nullable=True),
    db.Column("user_id", db.ForeignKey("user.id"), nullable=True),
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref='posts', lazy=True)
    title = db.Column(db.String, nullable=False)
    body = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    like = db.relationship("User", secondary=associate_post_likes)