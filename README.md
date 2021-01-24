# django-orm

A Python library that enables you to harness the power of Django's ORM in standalone
Python scripts.

Documentation: https://django-orm.readthedocs.io

## Installation

```
$ pip install django-orm
```

## Usage

Getting started with django-orm is quick and easy.

1. Create a Django app in your project's root directory:

    ```
    $ django-orm startapp
    ```

2. Create your models in `app-directory/models.py`:

    ```python
    from django.db import models
    
    # For demonstration purposes only.
    class ExampleModel(models.Model):
        exampleField = models.Field()
    ```

3. Make and apply your migrations:

    ```
    $ django-orm makemigrations
    ```
    ```
    $ django-orm migrate
    ```
 
4. Import the `orm_init()` function into your code and call it with the dunder variable `__file__` as its sole argument:

    ```python
    from django_orm import orm_init
    
    orm_init(__file__)
    ```

5. Finally, import your models:

    ```python
    # orm_init() must be imported AND called before this!
    
    from db import models  # Replace "db" with the name of your Django app if necessary
    
    # Do stuff with your models here
    ```

That's it.

This example doesn't demonstrate the full extent of django-orm's capabilities. 
You'll have to see the [documentation](https://django-orm.readthedocs.io) for that.

## Database Support

django-orm supports Oracle, PostgreSQL, and SQLite databases. A SQLite database connection comes configured for you,
and django-orm will use it by default if you don't add a different one yourself. More on adding database connections can
be found in the [documentation](https://django-orm.readthedocs.io).

## Additional Notes

django-orm is intended for people who are already familiar with Django's ORM; as such, the basics of how to use the
ORM are outside the scope of both this README and django-orm's [documentation](https://django-orm.readthedocs.io). If you're
looking to familiarize yourself with Django's ORM, see [Django's own documentation](https://docs.djangoproject.com/en/3.1/topics/db/),
particularly the sections on [models](https://docs.djangoproject.com/en/3.1/topics/db/models/) and [making queries](https://docs.djangoproject.com/en/3.1/topics/db/queries/).

## Attributions

django-orm is based on Dan Caron's [Django ORM Standalone Template](https://github.com/dancaron/Django-ORM).

"Django" is a registered trademark of the Django Software Foundation, which does not endorse this software.

## License

django-orm is released under the MIT License.
