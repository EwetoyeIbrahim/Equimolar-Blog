from flask import Flask
from flask_admin import Admin
from flask_fileupload import FlaskFileUpload
from models import Article, Tag, db, User, Role, ArticleAdmin, \
                    TagAdmin, UserAdmin, RoleAdmin
def create_app(config_object):
    app=Flask(__name__)
    app.config.from_object(config_object)
    db.init_app(app)
    db.reflect(app=app)
    # Initialize Flask-FileUpload.
    FlaskFileUpload(app)
    # Initialize Flask-Admin.
    admin = Admin(app)
    admin.add_view(ArticleAdmin(Article, db.session))
    admin.add_view(TagAdmin(Tag, db.session))
    admin.add_view(UserAdmin(User, db.session))
    admin.add_view(RoleAdmin(Role, db.session))
    # ----------- Initializations----------------------------------
    # Initialize the SQLAlchemy data store.
    from flask_security import Security, SQLAlchemyUserDatastore
    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    # Initialize Flask-Security.
    Security(app, user_datastore)
    from equimolar_blog.main_app import create_module
    with app.app_context():
        create_module(app)
    return app

