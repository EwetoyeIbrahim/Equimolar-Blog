from datetime import datetime
import json

from flask import render_template, request, abort, redirect, \
    url_for, flash
from werkzeug.urls import url_parse
from flask_security import Security, SQLAlchemyUserDatastore, \
    utils, login_required, login_user, logout_user, current_user
from flask_admin import Admin
from flask_fileupload import FlaskFileUpload
from markdown import markdown

from . import app
from .models import Article, Tag, db, User, Role, articles_tags
from .forms import ArticleForm, LoginForm, RegistrationForm
from .utilities import split_article, update_article, can_edit
# ----------- Initializations----------------------------------
# Initialize the SQLAlchemy data store.
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
# Initialize Flask-Security.
Security(app, user_datastore)
# Initialize Flask-Admin.
Admin(app)
# Initialize Flask-FileUpload.
FlaskFileUpload(app)

# ------- Setting up some dummy data for testing purpose ---
''' Note that this section must be deleted before moving into
a production environment, They are just here for testing purpose
'''
# Executes before the first request is processed.
@app.before_first_request
def before_first_request():
    '''
    Before doing anything, We have to make sure that our database is set
    Note, a blank database must exist before running, but if its an sqlite database
    it will be created on the fly if it does not exist.
    After creating all the tables, we will be setting up two stuffs:
    First we will create the roles:
    Four roles are provided here:
    Name        |       Description
    ________________________________
    Authour     |   Write and Edit own posts 
    Editor      |   Edit all posts (Post Table)
    Registrar   |   Create and Delete users (User Table)
    
    Some dummy users will be created and assigned roles: The names and roles
    of the dummy users are as stated above, i.e,
    Authour is assigned username='Authour', email='author@example.com', and
    password='password'
    '''

    # Create any database tables that don't exist yet.
    db.create_all()

    # Create the Roles
    user_datastore.find_or_create_role(name='Authour',description='Write and Edit own posts')
    user_datastore.find_or_create_role(name='Editor', description='Edit all posts')
    user_datastore.find_or_create_role(name='Registrar', description='Create and Delete users')
    
    
    #--- Delete this section before going public !!!
    # Create four Users for testing purposes -- unless they already exists.
    # In each case, use Flask-Security utility function to encrypt the password.
    default_users = {
        'Authour User':['authour@example.com', 'password', 'Authour'],
        'Editor User':['editor@example.com', 'password', 'Editor'],
        'Registrar User':['registrar@example.com', 'password', 'Registrar'],
        'Owner User':['owner@example.com', 'password', 'Registrar', 'Editor', 'Authour'],
    }
    for username, detail in default_users.items():
        
        if not user_datastore.get_user(detail[0]):
            user_datastore.create_user(username=username, email=detail[0],
                                       password=utils.encrypt_password(detail[1]),)
        # Assign roles to this user
        for i in detail[2:]:
            user_datastore.add_role_to_user(detail[0], i )
    # Save details to database
    db.session.commit()
# ------- End of dummy data for set-up ------------------------------

# -------- Error Handlers --------------------------------------------

@app.errorhandler(404)
def page_not_found(error):
    db.session.rollback()
    title = str(error)
    message = error.description
    return render_template('equimolar/errors.html',
                           title=title,
                           message=message),404

@app.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    title = error
    message = error.description
    return render_template('equimolar/errors.html',
                           title=title,
                           message=message),500

# -------- Endpoints -------------------------------------------------
@app.route('/')
def index():
    pagination = Article.query.order_by(Article.last_mod_date.desc()).paginate(1)
    return render_template('equimolar/index.html',
                           pagination=pagination)

@app.route('/register/', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.has_role('Registrar'):
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Congratulations, you have created a new registered user!')
            return redirect(url_for('index'))
        return render_template('equimolar/register.html', title='Register', form=form)
    flash('''Sorry, only users that has been given the Registrar role 
          can register a new user, Kindly contact Ewetoye Ibrahim for
          rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('register'))

@app.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@app.route('/<slug>')
def show_article_post(slug):
    '''
    Renders article with the related articles.
    Articles are based on slug, while#
    related articles are based on tags.
    Note: All articles are stored in Markdown syntax, thus, 
    they must be converted html before rendering
    '''
    article = Article.query.filter_by(slug=slug).first()
    if article==None:
        abort(404)
    article.content = markdown(article.content)
    # Getting the related articles based on tags,
    tag_names = [x.name for x in article.tags]
    related_articles = Article.query.filter(
                        Article.tags.any(Tag.name.in_(tag_names))).order_by(
                        Article.last_mod_date.desc()).all()  
    return render_template('equimolar/post_slug.html',
                           article = article,
                           related_articles = related_articles)

@app.route('/tags')
def show_tags():
    # Displays all available tags
    tags = Tag.query.all()
    return render_template('equimolar/tags.html',
                           tags=tags)

@app.route('/tag/<id>')
def show_tag(id):
    # Given a tag, all associated posts are displayed
    tag = Tag.query.get_or_404(id)
    articles = tag.articles.all()
    return render_template('equimolar/tag.html', tag=tag, entries=articles)


@app.route('/writter/', methods=['GET', 'POST'])
@login_required
def writter():
    '''
    View for writing and editing articles/posts.
    By mere hitting this endpoint, a logged-in user with aurthour rigth
    will be presented a blank form to write a new article.
    If the query of article_id(id of a specific post) is provided, typically by
    clicking on edit this post button which is only visible if the user is
    logged in and posses an authour right, the user is presented a form
    with the provided article_id information for editing.
    
    :param article_id: An optional query for editing an already published post
    :type article_id: str
    '''
    if (current_user.has_role('Authour') or current_user.has_role('Editor')) :
        article_id = request.args.get('article_id',None)
        form = ArticleForm()
        article_ = Article.query.filter(Article.id==article_id).first()
        editable = True
        if article_:
            editable = can_edit(current_user, article_.authour.first().username)

        if editable:     
            if request.method == 'POST':
                usname = User.query.filter_by(username=current_user.username)
                if article_:
                    print('I have Id')
                    article = update_article(form, article_, usname)
                    #db.session.delete(g.article_)
                else:
                    article = Article(
                        title=form.title.data,
                        slug=form.slug.data,
                        summary=form.summary.data,
                        content=form.content.data,
                        last_mod_date=form.last_mod_date.data,
                        authour=usname,
                    )

                list_tags = [x.strip() for x in form.tags.data.split(',')]
                for x in list_tags:                                             
                    new_tag = Tag.query.filter(Tag.name==x).first()
                    if new_tag is None:
                        new_tag = Tag(name=x)
                        db.session.add(new_tag)
                    article.tags.append(new_tag)
                db.session.commit()

                flash('Congratulations, your post was succesufully submitted')
                return redirect(f'/{article.slug}')

            else:
                if article_:
                    #g.article_ = article_
                    form = split_article(article_, form)
                return render_template('equimolar/writter.html', form=form, article_id=article_id)
        flash(''' Come on !!!, You can either edit your own post  or request for an
                Editor rigth.
                ''', 'error')
        logout_user()
        return redirect(url_for('writter'))

    flash('''Sorry, only users that has been given either Authour or Editor
            permissions can create or edit a post, Kindly contact Ewetoye Ibrahim for
            rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('writter'))