"""
Various utility functions.
"""

import os

import click
import toml

lib_root = os.path.dirname(__file__)

orm_settings = toml.load(os.path.join(lib_root, "orm-settings.toml"))


def get_settings() -> dict:
    """
    Gets django-orm's settings (orm-settings.toml, NOT to be confused with Django's settings.py).

    :return: A dictionary of django-orm's settings.
    """
    return orm_settings


def save_settings():
    """
    Converts ``orm_settings`` into a TOML-formatted string which is then written to orm-settings.toml,
    overwriting its current contents.
    """
    toml.dump(orm_settings, open(os.path.join(lib_root, "orm-settings.toml"), "w"))


def set_pythonpath(path: str):
    """
    Sets the PYTHONPATH environment variable to the value of ``path``.

    :param path: A filepath.
    """
    os.environ["PYTHONPATH"] = path


def selection_prompt(prompt: str, choices: list) -> str:
    """
    Prompts the user to select an option from an list of choices.

    :param prompt: The text of the prompt.
    :param choices: A list of choices.
    :return: The user's selection.
    """
    joiner = "\n* "
    selection = click.prompt(f"\n{prompt}\n\n"
                             f"* {joiner.join(choices)}",
                             type=click.Choice(choices, case_sensitive=False),
                             show_choices=False,
                             prompt_suffix="\n\n> ")

    return selection.casefold()


def get_connection_list(include_default: bool = True, current: bool = False) -> list:
    """
    Gets a list of existing database connections.

    :param include_default: If False, the default database connection will not be included in the returned list.
    :param current: If True, only the current database connection will be returned.
    :return: A list of existing database connections.
    """
    if current:
        db_list = [orm_settings["config"]["db_name"]]
    else:
        db_list = list(orm_settings["databases"].keys())

    if not include_default:
        db_list.remove("default")

    return db_list
