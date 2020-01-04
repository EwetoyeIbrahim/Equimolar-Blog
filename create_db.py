'''
Posses two functions:
create_role, which adds roles three roles if not found
create_dummy_db, which adds dummy users to the db

Note: this file should never be called on a production database
as calling this file directly invokes the create_dummy_db() function
which adds four Users with varying priviledges as stated in the
create_dummy_db() docstring
'''


def create_roles(user_datastore, db):
    '''
    Before doing anything, We have to make sure that our database is set
    Note, a blank database must exist before running, but if its an sqlite
    database, it will be created on the fly if it does not exist.
    After creating all the tables, we will be setting up two stuffs:
    First we will create the roles:
    Four roles are provided here:
    Name        |       Description
    ________________________________
    Authour     |   Write and Edit own posts 
    Editor      |   Edit all posts (Post Table)
    Registrar   |   Create and Delete users (User Table)
    '''
    # Create the tables, if they don't exist
    db.create_all()
    # Create the Roles if they don't exist
    user_datastore.find_or_create_role(name='Authour',
                        description='Write and Edit own posts')
    user_datastore.find_or_create_role(name='Editor', description='Edit all posts')
    user_datastore.find_or_create_role(name='Registrar',
                                        description='Create and Delete users')
    db.session.commit()

def create_dummy_db():
    '''
    Some dummy users will be created and assigned roles: The names and roles
    of the dummy users are as stated above, i.e,
    Authour is assigned username='Authour', email='author@example.com', and
    password='password'
    '''
    from flask_security import utils, SQLAlchemyUserDatastore
    from equimolar_blog.models import db, User, Role
    from run import app
    with app.app_context():
        # Create any database tables that don't exist yet.
        #db.create_all()
        # Indexing to articles to be search ready
        #flask_whooshalchemy.search_index(app, Article)
        user_datastore = SQLAlchemyUserDatastore(db, User, Role)
        # Create the Roles
        create_roles(user_datastore,db)
        # Create four Users for testing and debugging purposes -- unless they already
        # exists.
        # In each case, use Flask-Security utility function to encrypt the password.
        default_users = {
            'Authour User':['authour@example.com', 'password', 'Authour'],
            'Editor User':['editor@example.com', 'password', 'Editor'],
            'Registrar User':['registrar@example.com', 'password', 'Registrar'],
            'Owner User':['owner@example.com', 'password', 'Registrar', 'Editor',
                            'Authour'],
        }
        for username, detail in default_users.items():
            
            if not user_datastore.get_user(detail[0]):
                user_datastore.create_user(username=username, email=detail[0],
                                            password=utils.encrypt_password(detail[1]),)
            # Assign roles to this user
            for i in detail[2:]:
                user_datastore.add_role_to_user(detail[0], i )
        # ------- End of dummy data for set-up ------------------------------
        # Save details to database
        db.session.commit()

if __name__ == "__main__":
    create_dummy_db()