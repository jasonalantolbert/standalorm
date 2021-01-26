import os
import uuid

import dj_database_url
import standalorm.utils as utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

orm_settings = utils.get_settings()

# ascertain django app name and connection info
db_app = orm_settings["config"]["app"]
db_info = orm_settings["databases"][orm_settings["config"]["db_name"]]

# ascertain filepath for sqlite database if applicable
if db_info.get("ENGINE") == "django.db.backends.sqlite3":
    db_info["NAME"] = os.path.join(os.getenv("USER_ROOT"), db_info["NAME"])

if not db_info.get("USE_ENV", False):
    DATABASES = {"default": db_info}
else:
    DATABASES = {"default": dj_database_url.config(env=db_info["ENV_VAR"])}

INSTALLED_APPS = (
    db_app,
)

SECRET_KEY = uuid.uuid4()
