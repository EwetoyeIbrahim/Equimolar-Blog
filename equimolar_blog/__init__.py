import sys
import os
from flask import Flask
from flask_admin import Admin
import flask_whooshalchemy
from flask_fileupload import FlaskFileUpload
sys.path.append(os.path.abspath(os.path.dirname(__file__))) 
from models import Article, Tag, db, User, Role, ArticleAdmin, \
                    TagAdmin, UserAdmin, RoleAdmin
from config import config
from .main_app import create_module

def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    db.reflect(app=app)
    # Initialize Flask-FileUpload.
    FlaskFileUpload(app)
    flask_whooshalchemy.search_index(app, Article)
    # Initialize Flask-Admin.
    admin = Admin(app)
    admin.add_view(ArticleAdmin(Article, db.session))
    admin.add_view(TagAdmin(Tag, db.session))
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    # ----------- Initializations--------------------------------
    # Initialize the SQLAlchemy data store.
    from flask_security import Security, SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # Initialize Flask-Security.
    Security(app, user_datastore)
    with app.app_context():
        # Time to make sure roles exist in the database
        try:
            # the create_db.py file, may be deleted, to prevent the
            # creation of default roles.
            from create_db import create_roles
            create_roles(user_datastore, db)
        except ImportError:
            pass
        create_module(app)
    return app

