from os import environ

SECRET_KEY = environ.get('SECRET_KEY', None)
ADMIN_PASSWORD = environ.get('ADMIN_PASSWORD', None)
MAIL_USERNAME = environ.get('MAIL_USERNAME', None)
MAIL_PASSWORD = environ.get('MAIL_PASSWORD', None)

