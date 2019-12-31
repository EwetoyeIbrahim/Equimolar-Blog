from datetime import datetime
import json
import flask_whooshalchemy

from flask import render_template, request, abort, redirect, \
    url_for, flash, Blueprint
from flask_security import Security, SQLAlchemyUserDatastore, \
    utils, login_required, login_user, logout_user, current_user
'''from run import app'''
from models import Article, Tag, User, Role, articles_tags
from .forms import ArticleForm, LoginForm, RegistrationForm
from .utilities import blog_date, split_article, update_article, can_edit
from equimolar_blog import db


'''
# Executes before the first request is processed.
@app.before_first_request
def before_first_request():
    
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
    
    Some dummy users will be created and assigned roles: The names and roles
    of the dummy users are as stated above, i.e,
    Authour is assigned username='Authour', email='author@example.com', and
    password='password'
    

    # Create any database tables that don't exist yet.
    db.create_all()
    # Indexing to articles to be search ready
    flask_whooshalchemy.search_index(app, Article)

    # Create the Roles
    user_datastore.find_or_create_role(name='Authour',
                        description='Write and Edit own posts')
    user_datastore.find_or_create_role(name='Editor', description='Edit all posts')
    user_datastore.find_or_create_role(name='Registrar',
                                        description='Create and Delete users')
    
    
    #--- Delete this section before going public !!!
    # Create four Users for testing purposes -- unless they already exists.
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
'''

# -------- Error Handlers --------------------------------------------
blueprint = Blueprint('main', __name__)
blueprint.add_app_template_global(blog_date)
blueprint.add_app_template_global(can_edit)

@blueprint.errorhandler(404)
def page_not_found(error):
    db.session.rollback()
    title = str(error)
    message = error.description
    return render_template('equimolar/errors.html', title=title,
                           message=message),404

@blueprint.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    title = error
    message = error.description
    return render_template('equimolar/errors.html', title=title,
                           message=message),500

# -------- Endpoints -------------------------------------------------
@blueprint.route('/')
def index():
    pub_article = Article.public()
    pagination = pub_article.order_by(Article.last_mod_date.desc()).paginate(1)
    return render_template('equimolar/index.html',
                           pagination=pagination)

@blueprint.route('/register/', methods=['GET', 'POST'])
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
        return render_template('equimolar/register.html', title='Register',
                                form=form)
    flash('''Sorry, only users that has been given the Registrar role 
          can register a new user, Kindly contact Ewetoye Ibrahim for
          rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('register'))

@blueprint.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@blueprint.route('/<slug>')
def show_article(slug):
    '''
    Renders a published article with the given slug
    '''
    pub_article = Article.public()
    article = pub_article.filter_by(slug=slug).first()
    if article==None: abort(404)
    # Getting the related articles based on tags,
    tag_names = [x.name for x in article.tags]
    related = pub_article.filter(
                Article.tags.any(Tag.name.in_(tag_names))).order_by(
                Article.last_mod_date.desc()).limit(6).all()  
    return render_template('equimolar/post_slug.html',
                            article = article, related_articles = related)

@blueprint.route('/tags')
def show_tags():
    # Displays all available tags
    tags = Tag.query.all()
    return render_template('equimolar/tags.html',
                           tags=tags)

@blueprint.route('/tag/<id>')
def show_tag(id):
    # Given a tag, all associated published posts are displayed
    tag = Tag.query.get_or_404(id)
    articles = tag.articles.filter_by(draft=0).all()
    return render_template('equimolar/tag.html', tag=tag, entries=articles)


@blueprint.route('/writter/', methods=['GET', 'POST'])
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
            try:
                editable = can_edit(current_user, article_.authour.first().username)
            except:
                # an Exception will only be raised if the post is not assigned to a
                # user, thus in case of any Exception, only an Editor is permitted.
                if not current_user.has_role('Editor'): editable = False
        if editable:     
            if request.method == 'POST':
                usname = User.query.filter_by(username=current_user.username)
                if article_:
                    article = update_article(form, article_, usname)
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
                return render_template('equimolar/writter.html', form=form,
                                        article_id=article_id)
        flash(''' Come on !!!, You can either edit your own post  or request
                for an Editor right. You have been logged out!!!''', 'error')
        logout_user()
        return redirect(url_for('.writter'))

    flash('''Sorry, only users that has been given either Authour or Editor
            permissions can create or edit a post, Kindly contact the Admin
            for rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('.writter'))



@blueprint.route('/search', methods=['GET','POST'])
def search():
    '''
    Here, I am reusing the index template to serve the seach result
    '''
    pub_article = Article.public()
    request.query_string.decode("utf-8")
    q = request.form.get('search')
    results = pub_article.search(q).paginate(1)
    if results.items:
        return render_template('equimolar/index.html', pagination=results)
    flash('No result found', 'error')
    return redirect(url_for('.index'))
    
@blueprint.route('/draft')
@login_required
def drafts():
    slug=request.args.get('slug',None)
    draft_article = Article.in_draft()
    if slug:
        print(slug)
        article = draft_article.filter_by(slug=slug).first()
        if article==None: abort(404)
        # Getting the related articles based on tags,
        tag_names = [x.name for x in article.tags]
        related = draft_article.filter(
                    Article.tags.any(Tag.name.in_(tag_names))).order_by(
                    Article.last_mod_date.desc()).limit(6).all() 
        return render_template('equimolar/post_slug.html',
                            article = article, related_articles = related)
    
    pagination = draft_article.order_by( Article.last_mod_date.desc()).paginate(1)
    return render_template('equimolar/index.html',
                           pagination=pagination, drafts=True)

