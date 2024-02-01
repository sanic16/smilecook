from dotenv import load_dotenv
import os

load_dotenv()

mysql_db = {
    'user': os.getenv('USER_DB'),
    'password': os.getenv('PASSWORD_DB'),
    'host': os.getenv('HOST_DB'),
    'port': 3306,
}

print(os.getenv('MAIL_DEFAULT_SENDER'))

class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        mysql_db['user'],
        mysql_db['password'],
        mysql_db['host'],
        mysql_db['port'],
        'hg8ixodvba070fq0'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = '90e009fbad02c5d8c5db22a3ba55fb3deb870cb40bc54c1efaa8ecece67929700c3c06246e13e26835f55a5ee3fab16992222cc49df777eeb79f5e3019f2cd70'
    JWT_ERROR_MESSAGE_KEY = 'message'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    SECRET_KEY = 'top-secret'
    MAIL_SERVER = 'smtp.sendgrid.net'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'apikey'
    MAIL_PASSWORD = os.environ.get('SENDGRID_API_KEY')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    UPLOADED_IMAGES_DEST = 'client/assets/images'
