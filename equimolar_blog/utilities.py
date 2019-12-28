from . import app
from slugify import slugify

def blog_date(dateobj):
    '''
    converts a date into the blog's format rigth from Jinja2
    :param dateobj: datetime
    :param dateobj: datetime object
    '''
    return dateobj.strftime('%b %d, %Y')

def split_article(article, form):
    '''
    assign the contents of an article to
    the form fields, ready to be edited
    :param form: form response
    :type form: object
    :param article: article to be edited
    :type article: object
    '''
    form.title.data = article.title
    form.slug.data = article.slug
    form.summary.data = article.summary
    form.content.data = article.content
    form.last_mod_date.data = article.last_mod_date
    form.tags.data = ', '.join([tag.name for tag in article.tags])
    return form

def update_article(form, article, username):
    '''
    Updates an existing article
    :param form: form response
    :type form: object
    :param article: article to be edited
    :type article: object
    :param username: current editor
    :type username: str
    '''
    article.title = form.title.data
    if form.slug.data:
        article.slug = slugify(form.slug.data)
    else:
        article.slug = slugify(form.title.data)
    article.summary = form.summary.data
    article.content = form.content.data
    article.last_mod_date = form.last_mod_date.data
    '''
    Based on what I need, I want an article to be attributed
    the starting authour of a post.
    If you want the post to be attributed to the last post
    person who edited the article, just uncomment the line below
    article.authour=username
    '''
    # For now, the only way I know how to deal with tags is
    # to set the tags to empty and then add it again from the
    # view function, I will definately read-up on this
    article.tags=[]
    return article

def can_edit(current_user, authour):
    '''
    Checks if a post is editable, returns True if either the
    accessing user is the authour of the post or is an Editor,
    It is also made a global jinja function as it is also used to
    determine if an Edit button should be visible to the web user.
    :param current_user: Flask-Security extended Flask-Login current
                         user object
    :type current_user: object
    param authour: The authour of the given article
    :type authour: str
    '''
    if current_user.is_authenticated:
        if current_user.has_role('Editor'):
            return True
        if authour==current_user.username:
            return True
    return False


# These set of variable will called directly from templates
app.jinja_env.globals['blog_date'] = blog_date
app.jinja_env.globals['can_edit'] = can_edit