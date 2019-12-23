from . import app

def blog_date(dateobj):
    return dateobj.strftime(
        '%b %d, %Y')

app.jinja_env.globals['blog_date'] = blog_date