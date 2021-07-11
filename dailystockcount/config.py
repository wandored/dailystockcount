import os
import json

with open('/etc/config.json') as config_file:
    config = json.load(config_file)


class Config:
    SECRET_KEY = config.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = config.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = config.get('EMAIL_SERVER')  # Need to update config file
    MAIL_PORT = config.get('EMAIL_PORT')      # Need to update config file
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = config.get('EMAIL_USER')
    MAIL_PASSWORD = config.get('EMAIL_PASS')
    MAIL_DEFAULT_SENDER = 'chefk@dailystockcount.com'
