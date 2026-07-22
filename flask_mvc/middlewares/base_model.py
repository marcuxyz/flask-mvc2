from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import DeferredReflection
from sqlalchemy.exc import OperationalError, InvalidRequestError


# The base model that your classes will inherit
class BaseModel(DeferredReflection):
    """SQLAlchemy base model with deferred table reflection.

    This class is abstract and serves as a base for models that need to support
    runtime table reflection using
    :class:`sqlalchemy.ext.declarative.DeferredReflection`.
    """

    __abstract__ = True


class FlaskReflection:
    """Helper to initialize SQLAlchemy reflection in a Flask application.

    This class encapsulates the logic to prepare reflected tables via
    :meth:`BaseModel.prepare` when the SQLAlchemy extension is available
    in the Flask app context.
    """

    def __init__(self, app: Flask = None, db: SQLAlchemy = None):
        if app is not None and db is not None:
            self.init_app(app, db)

    def init_app(self, app: Flask, db: SQLAlchemy):
        """Initialize model reflection for a Flask application.

        Args:
            app: Instance of :class:`flask.Flask` where reflection will be initialized.
            db: Instance of :class:`flask_sqlalchemy.SQLAlchemy` used to obtain the
                engine and prepare reflected models.

        Raises:
            ValueError: If ``db`` is ``None``.
        """
        if db is None:
            raise ValueError("FlaskReflection required a instance of SQLAlchemy")

        with app.app_context():
            try:
                BaseModel.prepare(db.engine)
            except (OperationalError, InvalidRequestError):
                app.logger.info(
                    "[FlaskReflection] Deferred introspection: tables or database not "
                    "found. This is normal on the first migration."
                )
