import os

# --- Enabling Some Flask Default Protection like CSRF -------
SECRET_KEY = os.urandom(32)

# ---------------- Database ----------------------------------
SQLALCHEMY_DATABASE_URI = 'sqlite:///test5.db'

# ---------------- Flask Security ----------------------------
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
SECURITY_PASSWORD_SALT = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'

# ---------------- Flask Mial -------------------------
'''
Flask-Security optionally sends email notification to users upon registration, password reset, etc.
It uses Flask-Mail behind the scenes.
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

# -------- Some Site Configurations -------------------------------
SITE_KEYWORDS = ['Data Analysis', 'Nigerian Data', 'Data Dashboard']
SITE_NAME = 'Equimolar'