import os

from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='a430f7c71eba782cbf4d9c434df76a6850cb9d7322f14598495b995c0d53e21e',
        SQLALCHEMY_DATABASE_URI='sqlite:///blog.db',
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    
    from . import posts
    from . import auth
    app.register_blueprint(posts.bp)
    app.register_blueprint(auth.bp)

    app.add_url_rule('/', endpoint='index')

    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from blog.db import db
    db.init_app(app)
    db.create_all(app=app)

    return app