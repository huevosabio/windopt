import os


# get db uri from env variables, if not found assume there is a mongo instance locally.

DB_URI = os.getenv('MONGO_URI','localhost')

DB_USER =os.getenv('DB_USER',None)
DB_PWD =os.getenv('DB_PWD',None)

ENV_NAME =  os.getenv('ENV_NAME', None)

CSRF_ENABLED = True
SECRET_KEY = 'titi'

