"""Custom exceptions for Flask MVC CLI."""


class FlaskMVCError(Exception):
    """Base exception for Flask MVC CLI errors."""

    pass


class ControllerGenerationError(FlaskMVCError):
    """Exception raised when controller generation fails."""

    pass


class TemplateNotFoundError(FlaskMVCError):
    """Exception raised when template file is not found."""

    pass


class InvalidControllerNameError(FlaskMVCError):
    """Exception raised when controller name is invalid."""

    pass


class RoutesModuleNotFoundError(FlaskMVCError):
    """Exception raised when routes module cannot be imported."""

    pass
