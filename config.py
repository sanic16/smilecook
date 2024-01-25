from dotenv import load_dotenv
import os

load_dotenv()

mysql_db = {
    'user': os.getenv('USER_DB'),
    'password': os.getenv('PASSWORD_DB'),
    'host': os.getenv('HOST_DB'),
    'port': 3306,
}

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
    mysql_db['user'],
    mysql_db['password'],
    mysql_db['host'],
    mysql_db['port'],
    'hmlhi3b4fnfpqx4o'
)


class Config:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}'.format(
        mysql_db['user'],
        mysql_db['password'],
        mysql_db['host'],
        mysql_db['port'],
        'hmlhi3b4fnfpqx4o'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
