# Introduction

<p align="center">This extension facilitates the application of this design pattern in Flask </p>
<p align="center">
    <a href="https://github.com/marcuxyz/flask-mvc/actions/workflows/test.yml">
        <img src="https://github.com/marcuxyz/flask-mvc/actions/workflows/test.yml/badge.svg?branch=main" alt="unit test" height="18">
    </a>
    <a href="https://badge.fury.io/py/flask-mvc">
        <img src="https://badge.fury.io/py/flask-mvc.svg" alt="PyPI version" height="18">
    </a>
</p>


Designed to allow developers to implement the Model-View-Controller (MVC) design pattern in Flask applications with the help of this extension.
<hr />

Install Flask MVC using pip:

```shell
$ pip install flaskmvc
```

Install Flask MVC using UV:

```shell
$ uv add flaskmvc
```

Now, let's get started:

```python
from flask import Flask
from flask_mvc import FlaskMVC
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

    # registering extensions
    FlaskMVC(app)
    db.init_app(app)

    return app
```

![Image of structure](assets/images/structure.png)

## Features

Flask MVC builds on provides the best architecture experience for Flask, and gives you:

- You can directories as controllers, models, and views.
- It Supports the controllers' creation, and you can separate the logic of your application of business rules
- You can separate routes of business rules
- You can use the before_action to execute a specific code
- You can integrate with other extensions of Flask, Flask-SQLAlchemy, Flask-Migrate, etc.
- **SQLAlchemy Introspection**: deferred model reflection support with `ReflectedModel` and `FlaskReflection` for runtime schema discovery.

## Dependencies

Flask MVC just depends on the Flask extensions to working and requires Python >=3.8.0,<4.0.0.

## SQLAlchemy Introspection

This extension now supports deferred SQLAlchemy reflection for models. By inheriting from `ReflectedModel` and using the `FlaskReflection` integration, models can map to existing database tables without declaring every column in the model class.

Example:

```python
from flask_mvc.middlewares.base_model import ReflectedModel
from tests.app import db

class Message(ReflectedModel, db.Model):
    __tablename__ = 'messages'
```

Initialize the database extension before Flask MVC so introspection works correctly:

```python
from flask import Flask
from flask_mvc import FlaskMVC
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

db.init_app(app)
FlaskMVC(app, path='app', db=db)
```
