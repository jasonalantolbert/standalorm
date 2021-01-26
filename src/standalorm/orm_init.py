"""
Provides a function for initializing standalorm.
"""


import sys

sys.dont_write_bytecode = True

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "standalorm.settings")

import django
from path import Path


def orm_init(file_dunder):
    """
    Initializes standalorm. This function is the only thing from the library a typical end user should be importing
    into their code.

    This function should ideally be called at the beginning of the user's code, but strictly speaking,
    only has to be called before the user imports their models. (To clarify, this function doesn't have to be called
    every single time a model is imported; just one call somewhere in the execution process is enough).

    This function should never ever ever be called from models.py or it will probably break something.

    :param file_dunder: ``orm_init()`` should always be called with the dunder variable ``__file__`` as its sole
                         argument. This is used to ascertain the directory from which the function is being called so
                         standalorm knows where to look for the SQLite database, if one is in use. While this parameter
                         isn't strictly necessary when a non-SQLite database is being used, passing it in regardless
                         does no harm and it's easier for the end user to just always pass it in without having to
                         worry about what database is being used.
    """
    os.environ["USER_ROOT"] = os.path.dirname(file_dunder)

    with Path(os.path.dirname(__file__)):
        django.setup()
