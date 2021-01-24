"""
django-orm's command line interface.
"""

import os
import subprocess
import sys
import uuid
from tempfile import TemporaryDirectory

import click
import colorama
import django_orm.utils as utils
import toml
from colorama import Fore
from django_orm.db_makers import make_new_db
from path import Path

colorama.init(autoreset=True)

lib_root = os.path.dirname(__file__)
user_root = os.getcwd()

orm_settings = utils.get_settings()


@click.group()
def cli():
    """
    django-orm is a Python library that enables you to harness the power of Django's ORM in standalone Python scripts.

    https://github.com/jasonalantolbert/django-orm
    """
    pass


@cli.command()
@click.option("--license", "-l", "show_license", is_flag=True, help="Display the full license text.")
def about(show_license=False):
    """
    Display license and copyright information.
    """
    if not show_license:
        print(f"\ndjango-orm Copyright (c) 2021 Jason Tolbert Jr.\n"
              f"\n"
              f"django-orm is released under the MIT License. See the full license text \n"
              f"by running {Fore.CYAN + 'django-orm about --license' + Fore.RESET}.\n"
              f"\n"
              f"'Django' is a registered trademark of the Django Software Foundation, which \n"
              f"does not endorse this software.\n")
    else:
        with open(os.path.join(lib_root, "LICENSE.md")) as license_file:
            print(f"\n{license_file.read()}\n")


@cli.command()
@click.argument("app_name", required=False, default="db")
@click.option("--no-create", "-nc", "no_create", is_flag=True,
              help="Don't create a new folder or the __init__.py and models.py files. Use this if you need to point "
                   "django-orm to an existing app directory without creating a new one.")
def startapp(app_name: str, no_create: bool = False):
    """
    Create a Django app in your project's root directory.
    """
    orm_settings["config"]["app"] = app_name  # set app name

    if not no_create:
        # create app directory
        app_path = os.path.join(user_root, app_name)
        os.mkdir(app_path)

        # populate app directory with __init__.py and models.py
        with Path(app_path):
            open("__init__.py", "w")

            with open("models.py", "w") as models:
                with open(os.path.join(lib_root, "models_template.py")) as template:
                    models.write(template.read())

    utils.save_settings()

    print(f"\nApp '{app_name}' started successfully.\n")


@cli.command()
def makemigrations():
    """
    Create database migrations.
    """
    app_name = orm_settings["config"]["app"]
    os.environ["USER_ROOT"] = user_root
    utils.set_pythonpath(user_root)

    with Path(lib_root):
        print()
        subprocess.run(f"python manage.py makemigrations {app_name}")
        print()


@cli.command()
def migrate():
    """
    Apply database migrations.
    """
    app_name = orm_settings["config"]["app"]
    os.environ["USER_ROOT"] = user_root
    utils.set_pythonpath(user_root)

    with Path(lib_root):
        print()
        subprocess.run(f"python manage.py migrate {app_name}")
        print()


@cli.command()
def pycharm():
    """
    Get information on enabling Django support in PyCharm.
    """
    print(f"\nIf you're using PyCharm Professional, you can enable Django support in PyCharm's settings to enhance \n"
          f"the IDE's code completion abilities when it comes to your models. (This functionality is not supported \n"
          f"by PyCharm Community or PyCharm Edu.)\n"
          f"\n"
          f"Go to Settings > Languages & Frameworks > Django, check 'Enable Django Support', and provide the \n"
          f"following information:\n"
          f"\n"
          f"Project root: {lib_root}\n"
          f"Settings: {os.path.join(lib_root, 'settings.py')}\n"
          f"Manage script: {os.path.join(lib_root, 'manage.py')}\n")


@cli.group()
def db():
    """
    Manage database connections.
    """
    pass


@db.command()
@click.argument("db", required=False, default="")
@click.option("--env", "use_env", is_flag=True,
              help="Configure the connection using a URI environment variable (Oracle "
                   "and PostgreSQL only.)")
def add(db: str, use_env: bool = False):
    """
    Add a new database connection.
    """
    db = db.casefold()

    db_choices = ["Oracle", "PostgreSQL", "SQLite"]

    if use_env:
        db_choices.remove("SQLite")

    # prompt user for connection name if not specificed in command line
    if not db:
        db = utils.selection_prompt("Choose a database:", db_choices)
    elif db not in [choice.casefold() for choice in db_choices]:
        print(Fore.RED + f"\nThat's not a valid database. django-orm supports {', '.join(db_choices[:-1])} "
                         f"and {db_choices[-1]}.\n")
        exit()

    # start interactive database creation prompt
    db_info = make_new_db(db, use_env)

    print(f"\nChoose a name for this database connection. This name will be used to identify the \n"
          f"database to both django-orm and you, so make sure it's both unique and easily\n"
          f"recognizable. django-orm will generate a random name if you leave this empty.\n"
          f"(Enter !names to see what names you can't use.)")

    while True:
        existing_names = {name.casefold() for name in orm_settings["databases"].keys()}

        # prompt user for connection name
        db_name = click.prompt("> ", prompt_suffix="", default=str(uuid.uuid4()), show_default=False).casefold()

        if db_name == "!names":  # display used connection names
            print("\nThe following names are being used by other database connections "
                  "and can't be used for this one:\n")
            for name in existing_names:
                print(f"* {name}")

            # restart loop
            print("\nChoose a name for this database connection:")
            continue

        if db_name in existing_names:  # enforce name uniqueness
            print(Fore.RED + "\nThe name must be unique.")

            # restart loop
            print("Choose a name for this database connection:")
            continue
        else:  # save connection settings
            db_entry = {db_name: db_info}
            orm_settings["databases"].update(db_entry)
            utils.save_settings()
            break

    print(f"\nDatabase connection '{db_name}' successfully added.\n")


@db.command()
@click.argument("db", required=False, default="")
def switch(db: str):
    """
    Switch to a different database connection.
    """
    db = db.casefold()
    db_choices = utils.get_connection_list(include_default=True)

    # prompt user for connection name if not specified in command line and multiple connections exist
    if not db and len(db_choices) > 1:
        db = utils.selection_prompt("Which database connection would you like to switch to?", db_choices)

    if len(db_choices) <= 1:
        print(Fore.RED + "\nThere are currently no database connections you can switch to.\n")
    elif db not in db_choices:
        print(Fore.RED + "\nThere's no database connection with that name.\n")
    else:
        # set new connection
        orm_settings["config"]["db_name"] = db
        utils.save_settings()

        print(f"\nDatabase connection switched to '{db}'.\n")


@db.command()
@click.argument("db", required=False, default="")
def edit(db: str):
    """
    Edit an existing database connection.
    """
    db = db.casefold()
    db_choices = utils.get_connection_list(include_default=False)

    # prompt user for connection name if not specified in command linea
    if not db and db_choices:
        db = utils.selection_prompt("Which database connection would you like to edit?", db_choices)

    if db not in db_choices:
        if not db_choices:
            print(Fore.RED + "\nThere are currently no database connections you can edit.\n")
        else:
            print(Fore.RED + "\nThere's no database connection with that name.\n")
    else:
        connection = orm_settings["databases"][db]  # get settings of specified connection

        engine = connection.pop("ENGINE")  # remove ENGINE key from dictionary to prevent user modification

        with TemporaryDirectory() as tmpdir:  # create temporary directory
            tmp_filepath = os.path.join(tmpdir, f"{uuid.uuid4()}.txt")  # create TXT file inside temporary directory

            # write connection info to TXT file
            with open(tmp_filepath, "w") as file:
                file.write("# (django-orm) Make your changes, then close the editor. DO NOT EDIT THIS LINE.\n\n")
                file.write(toml.dumps(connection))

            # open TXT file in system editor
            subprocess.run(tmp_filepath, shell=True)

            try:  # attempt to convert edited TXT file into a dictionary
                edited_connection = toml.loads("".join(open(tmp_filepath).readlines()[1:]))
            except toml.TomlDecodeError as tde:  # if conversion fails, print error message and exit
                print(Fore.RED + f"\nYour changes couldn't be saved. Please try again.\n"
                                 f"(TomlDecodeError: {tde})\n", file=sys.stderr)

                exit()

        # temporary directory is automatically deleted when the program exits the with block

        edited_connection["ENGINE"] = engine  # re-add ENGINE key
        orm_settings["databases"][db] = edited_connection

        utils.save_settings()

        print(f"\nChanges to database connection '{db}' saved successfully.\n")


@db.command()
@click.argument("db", required=False, default="")
def remove(db: str):
    """
    Remove an existing database connection.
    """
    db = db.casefold()
    db_choices = utils.get_connection_list(include_default=False)

    # prompt user for connection name if not specified in command line
    if not db and db_choices:
        db = utils.selection_prompt("Which database connection would you like to remove?", db_choices)

    if db not in db_choices:
        if not db_choices:
            print(Fore.RED + "\nThere are currently no database connections you can remove.\n")
        else:
            print(Fore.RED + "\nThere's no database connection with that name.\n")
    else:
        # switch to default connection if current connection is set to be removed
        if orm_settings["config"]["db_name"] == db:
            orm_settings["config"]["db_name"] = "default"

        orm_settings["databases"].pop(db)

        utils.save_settings()

        print(f"\nDatabase connection '{db}' successfully removed.\n")


@db.command()
@click.option("--current", "-c", "current", is_flag=True, help="List only the current connection.")
def ls(current: bool = False):
    """
    List existing database connections.
    """
    print()

    connections = utils.get_connection_list(include_default=True, current=current)

    for conn in connections:
        print(f"* {conn}")

    print()


if __name__ == '__main__':
    cli()
