"""
Interactive prompts for adding new database connections.
"""

import os
import re
import sys
from getpass import getpass

import click
import django
from colorama import Fore
from pathvalidate import is_valid_filepath

docs_version = re.findall("^\d\.\d", django.get_version())[0]
docs_url = f"https://docs.djangoproject.com/en/{docs_version}/ref/databases"


def env_config() -> dict:
    """
    Configures a database connection using an environment variable (Oracle and PostgreSQL only).

    :return: A dictionary containing information about the newly-created database connection.
    """
    env_var = input(
        "\nIdentify the name of the environment variable the connection URI will be bound to. You will have to \n"
        "set this environment variable manually outside of django-orm, and the name must match EXACTLY \n"
        "what you input here (including case sensitivity).\n"
        "> "
    )

    db_info = {
        "USE_ENV": True,
        "ENV_VAR": env_var
    }

    return db_info


def oracle(use_env: bool) -> dict:
    """
    Creates a new Oracle database connection.

    :param use_env: If True, the connection will be configured using a URI environment variable.
    :return: A dictionary containing information about the newly-created database connection.
    """
    if use_env:
        db_info = env_config()
    else:
        print(f"\nPlease read Django's documentation for Oracle databases before proceeding. It contains\n"
              f"important information you'll need to keep in mind when setting up the database connection.\n"
              f"{docs_url}/#oracle-notes")

        input("\nPress Enter to continue.")

        print("\nPlease provide the following information about the Oracle database:\n")

        db_info = {
            "ENGINE": "django.db.backends.oracle",
            "NAME": input("Name: "),
            "USER": input("User: "),
            "PASSWORD": getpass("Password: "),
            "HOST": input("Host: "),
            "PORT": input("Port: ")
        }

    threaded = click.confirm("\nSet threaded option to true? (If you're unsure or don't know what this means, say no.)",
                             prompt_suffix="\n> ")

    db_info.update({
        "OPTIONS": {
            "threaded": threaded}
    })

    return db_info


def postgresql(use_env: bool) -> dict:
    """
    Creates a new PostgreSQL database connection.

    :param use_env: If True, the connection will be configured using a URI environment variable.
    :return: A dictionary containing information about the newly-created database connection.
    """

    # check for psycopg2
    try:
        import psycopg2
    except ImportError:
        print(f"\nUsing PostgreSQL databases requires psycopg2, which django-orm was unable to find in your\n"
              f"environment. Install psycopg2 and try again.\n"
              f"\n"
              f"{Fore.CYAN + 'pip install psycopg2' + Fore.RESET}\n")

        exit()

    if use_env:
        db_info = env_config()
    else:
        print("\nPlease provide the following information about the PostgreSQL database:\n")

        db_info = {
            "ENGINE": "django.db.backends.postgresql_psycopg2",
            "NAME": input("Name: "),
            "USER": input("User: "),
            "PASSWORD": getpass("Password: "),
            "HOST": input("Host: "),
            "PORT": input("Port: "),
        }

    return db_info


def sqlite() -> dict:
    """
    Create a new SQLite database connection.

    :return: A dictionary containing information about the newly-created database connection.
    """
    user_root = os.getcwd()

    def validate_filepath(path):
        """
        Validates that the filepath at which the user has indicated the SQLite database should exist is a valid one
        for the user's operating system.

        :param path: A filepath.

        :return: True if the filepath is valid, False otherwise.
        """
        """
        
        """
        platforms = {
            "win32": "Windows",
            "darwin": "macOS",
            "linux": "Linux",
        }

        try:
            os_name = platforms[sys.platform]
        except KeyError:
            os_name = "universal"

        return is_valid_filepath(path, platform=os_name)

    print(f"\nEnter the path to an SQLite3 (.sqlite3) database. The path must be relative to {user_root}.\n"
          f"If no SQLite3 database exists at this path, django-orm will create one for you the first time you "
          f"apply migrations.\n")

    while True:
        path = input("> ")

        if not validate_filepath(path):  # validate filepath per OS requirements
            print("\nThat's not a valid filepath.")
            print("Enter the path to an SQLite3 database:")
            continue
        elif not path.endswith(".sqlite3"):  # validate filepath extension
            print("\nThat's not a valid SQLite3 database path (SQLite3 databases have the file extension .sqlite3).")
            print("Enter the path to an SQLite3 database:")
            continue
        elif not os.path.abspath(path).startswith(user_root):  # validate relativity to user root directory
            print(f"\nThe path must be relative to {user_root}.")
            print("Enter the path to an SQLite3 database:")
            continue
        else:
            break

    db_info = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": path
    }

    return db_info


def make_new_db(database, use_env) -> dict:
    """
    Calls either ``oracle()``, ``postgresql()``, or ``sqlite()`` depending on the value of ``database``.

    :param database: The database for which a connection is going to be created ("oracle", "postgresql", or "sqlite").
    :param use_env: If True, django-orm will prompt the user to configure the connection using a URI environment
                    variable (Oracle and PostgreSQL only).
    :return: A dictionary containing information about the newly-created database connection.
    """
    if database == "oracle":
        db_info = oracle(use_env)
    elif database == "postgresql":
        db_info = postgresql(use_env)
    else:
        db_info = sqlite()

    return db_info
