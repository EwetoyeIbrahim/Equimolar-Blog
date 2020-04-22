from datetime import datetime
import json, os, uuid

from flask import render_template, request, abort, redirect, \
    url_for, flash, Blueprint, current_app
from flask_security import Security, SQLAlchemyUserDatastore, \
    login_required, login_user, logout_user, current_user
from equimolar_blog import db, Article, Tag, User, Role
from .forms import ArticleForm, RegistrationForm
from .utilities import blog_date, split_article, update_article, \
    can_edit, can_create

# Declaring the blueprints ------------------------------------------

equimolar_bp = Blueprint('equimolar_blog', __name__)
# Template accessible variables
equimolar_bp.add_app_template_global(blog_date)
equimolar_bp.add_app_template_global(can_edit)
equimolar_bp.add_app_template_global(can_create)

# -------- Error Handlers --------------------------------------------
@equimolar_bp.errorhandler(404)
def page_not_found(error):
    db.session.rollback()
    title = str(error)
    message = error.description
    return render_template('equimolar/errors.html', title=title,
                        message=message),404

@equimolar_bp.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    title = error
    message = error.description
    return render_template('equimolar/errors.html', title=title,
                        message=message),500

# -------- Endpoints -------------------------------------------------
@equimolar_bp.route('/')
@equimolar_bp.route('/page/<int:page>')
def index(page=1):
    pub_article = Article.public()
    pagination = pub_article.order_by(Article.last_mod_date.desc()).paginate(page, per_page=50)
    return render_template('equimolar/index.html',
                        pagination=pagination)

@equimolar_bp.route('/register/', methods=['GET', 'POST'])
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
        can register a new user. Kindly contact Ewetoye Ibrahim for
        rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('register'))

@equimolar_bp.route('/logout/')
def logout():
    logout_user()
    return redirect('/')

@equimolar_bp.route('/<slug>')
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

@equimolar_bp.route('/tags')
def show_tags():
    # Displays all available tags
    tags = Tag.query.all()
    return render_template('equimolar/tags.html',
                        tags=tags)

@equimolar_bp.route('/tag/<tag_name>')
def show_tag(tag_name):
    # Given a tag, all associated published posts are displayed
    tag = Tag.query.filter_by(name=tag_name).first()
    if tag is not None:
        articles = tag.articles.filter_by(draft=0).all()
        return render_template('equimolar/tag.html', tag=tag, entries=articles)
    flash('Tag not found', 'error')
    return redirect(url_for('.index'))


@equimolar_bp.route('/writter/', methods=['GET', 'POST'])
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
                        draft=form.draft.data,
                    )

                list_tags = [x.strip() for x in form.tags.data.split(',')]
                for x in list_tags:
                    new_tag = Tag.query.filter(Tag.name==x).first()
                    if new_tag is None:
                        new_tag = Tag(name=x)
                        db.session.add(new_tag)
                    article.tags.append(new_tag)
                db.session.commit()
                if form.draft.data==False:
                    flash('Congratulations, your article has been published')
                    return redirect(f'/{article.slug}')
                else:
                    flash('Your Article has been saved to draft')
                    return redirect(f'/draft?slug={article.slug}')

            else:
                if article_:
                    form = split_article(article_, form)
                return render_template('equimolar/writter.html', form=form,
                                        article_id=article_id)
        flash(''' Come on !!!, You can either edit your own post  or request
                for an Editor right. You have been logged out!!!''', 'error')
        logout_user()
        return redirect(url_for('.writter'))

    flash('''Sorry, only users that has been given either Authour or Editor
            permissions can create or edit a post. Kindly contact the Admin
            for rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('.writter'))



@equimolar_bp.route('/search', methods=['GET','POST'])
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

@equimolar_bp.route('/draft')
@login_required
def drafts():

    if can_create(current_user):

        slug=request.args.get('slug',None)
        draft_article = Article.in_draft()
        if slug:
            article = draft_article.filter_by(slug=slug).first()
            if article==None: abort(404)
            # Getting the related articles based on tags,
            tag_names = [x.name for x in article.tags]
            related = draft_article.filter(
                        Article.tags.any(Tag.name.in_(tag_names))).order_by(
                        Article.last_mod_date.desc()).limit(11).all()
            return render_template('equimolar/post_slug.html',
                                article = article, related_articles = related)

        pagination = draft_article.order_by( Article.last_mod_date.desc()).paginate(1)
        return render_template('equimolar/index.html',
                            pagination=pagination, drafts=True)
    flash('''Sorry, only users that has been given either Authour or Editor
            permissions can see posts in draft. Kindly contact the Admin
            for rectification. You have been logged-out!!!.''', 'error')
    logout_user()
    return redirect(url_for('.index'))

# Not yet in use -------------------------------
@equimolar_bp.route('/featured_images', methods=['POST'])
def featured_image():
    # To be used later for uploading and assigning featured images
    if request.method == 'POST':
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1]
        # Only allow extensions in FEATURED_IMG_EXTENSIONS list in config
        print(extension)
        if extension.lower()[1:] in current_app.config['FEATURED_IMG_EXTENSIONS']:
            f_name = str(uuid.uuid4()) + extension
            featured_storage = current_app.config['EXT_FEATURED_IMG_PATH'] or 'Local'
            print(featured_storage)
            if featured_storage == 'Local':
                featured_storage = os.path.join(os.path.abspath(
                    os.path.dirname(__file__)),'static/featured_images')
            file.save(os.path.join(featured_storage, f_name))
            return json.dumps({'filename':f_name})
        return json.dumps({'Error':f'''Allowed featured image filetypes are {
            current_app.config['FEATURED_IMG_EXTENSIONS']}'''})
