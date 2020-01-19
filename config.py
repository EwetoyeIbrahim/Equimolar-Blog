import os

class Config:
    
    # -------- Some Site Configurations -------------------------------
    SITE_KEYWORDS = ['Data Analysis', 'Nigerian Data', 'Data Dashboard']
    SITE_NAME = 'Equimolar'

    # --- Some Flask Stuffs -------
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ---------------- Flask Security ----------------------------
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_PASSWORD_SALT = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

        
    # -------- Flask FileUpload ---------------------------
    '''
    The aim is to host just as few files as possible,
    most of the large files will be linked to, although we can
    host all files on our server but I prefer linking to them.
    For example, I can always link to Github files and Youtube videos
    instead hosting them on my server.
    If more extensions are required, you can always add to the list
    of allowed extensions, but if you want all the extensions in the
    whole world, just set:
    FILEUPLOAD_ALLOW_ALL_EXTENSIONs = True
    '''
    FILEUPLOAD_LOCALSTORAGE_IMG_FOLDER = 'uploaded_files'
    FILEUPLOAD_PREFIX = '/upload'
    FILEUPLOAD_ALLOWED_EXTENSIONS =['jpg', 'jpeg', 'png', 'gif',
                                    '3gp', 'mp3', 'mp4',
                                    'pdf', 'doc', 'docx', 'xls', 'xlsx',
                                    ]
    
    # -------- Facebook Comment ---------------------------
    '''
    Facebook comment will only be put to use if FACEBOOK_COMMENT is set
    to True. All the attributes declared here are as documented in facebook
    just prefixed with FB_
    '''
    FACEBOOK_COMMENT = False
    FB_DATA_COLORSCHEME = 'light' # ligth|dark
    FB_DATA_NUMPOSTS = '20'
    FB_DATA_ORDER_BY = 'social' # social|time|reverse_time
    FB_DATA_WIDTH = '100%'
    
    
class DevelopmentConfig(Config):
        # ---------------- Database ----------------------------------
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test5.db'
    # ---------------- Flask Mial -------------------------
    '''
    Flask-Security optionally sends email notification to users upon
    registration, password reset, etc. It uses Flask-Mail behind the scenes.
    Set mail-related config values.
    Replace this with your own 'from' address
    '''
    SECURITY_EMAIL_SENDER = 'admin@gmail.com'
    # Replace the next five lines with your own SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'admin@gmail.com'
    MAIL_PASSWORD = 'password'

    #------ Debug during development ----------
    DEBUG = True

class ProductionConfig(Config):
    # ---------------- Database ----------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DB_URI') or \
                                'sqlite:///equimolar.db'
    FACEBOOK_COMMENT = True

config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig,
}