import os

class Config:

    # -------- Some Site Configurations -------------------------------
    SITE_KEYWORDS = ['Data Analysis', 'African Data', 'Nigerian Data', 'Data Dashboard']
    SITE_DESCRIPTION = "" # Short meta description of the homepage
    SITE_NAME = 'Equimolar'
    ABOUT_LINK = 'https://ewetoyeibrahim.github.io/'

    # --- Some Flask Stuffs -------
    SECRET_KEY = os.urandom(32)
    SQLALCHEMY_TRACK_MODIFICATIONS = True

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
    FACEBOOK_COMMENT = True
    FB_DATA_COLORSCHEME = 'light' # ligth|dark
    FB_DATA_NUMPOSTS = '20'
    FB_DATA_ORDER_BY = 'social' # social|time|reverse_time
    #FB_DATA_WIDTH = '100%' # Moved to template


class DevelopmentConfig(Config):
    # ---------------- Database ----------------------------------
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test5.db'
    #------ Debug during development ----------
    DEBUG = True

class ProductionConfig(Config):
    # ---------------- Database ----------------------------------
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCTION_DB_URI') or \
                                'sqlite:///equimolar.db'
    #to enable debug mode, simply uncomment and provide the app id below
    #FACEBOOK_COMMENT_APPID = 'Your___App____Id'
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production' : ProductionConfig,
    'default' : DevelopmentConfig,
}