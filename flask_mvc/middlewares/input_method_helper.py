import markupsafe


class InputMethodHelper:
    """
    A middleware class for handling HTML-related operations, specifically for creating hidden input fields
    with specific methods (like PUT and DELETE) that are not natively supported by HTML forms.

    Methods:
    - _input_html: Private method to generate HTML input element.
    - _put: Private method to generate a hidden input field for the PUT method.
    - _delete: Private method to generate a hidden input field for the DELETE method.
    - method: Public method to handle the generation of appropriate HTML based on a given string.
    """

    def input_hidden_method(self, input_method):
        """
        Determines the appropriate HTML string to return based on the given method string.

        Args:
        - string (str): The method string (e.g., 'put', 'delete').

        Returns:
        - Markup: A markupsafe.Markup object containing the appropriate HTML string.
                  This object is safe to render directly in templates.
        """
        result = {
            "put": self._put(),
            "delete": self._delete(),
        }[input_method.lower()]

        return markupsafe.Markup(result)  #  nosec: B704

    def _input_html(self, input_method):
        """
        Generates a hidden HTML input element with proper escaping.

        Args:
        - input_method (str): The HTTP method to be used (e.g., 'put', 'delete').

        Returns:
        - str: A safe HTML string for a hidden input element with the specified method.
        """
        return f"<input type='hidden' name='_method' value={input_method.upper()}>"

    def _put(self):
        """
        Generates a hidden input field for the PUT method.

        Returns:
        - str: An HTML string for a hidden input element for the PUT method.
        """
        return self._input_html("put")

    def _delete(self):
        """
        Generates a hidden input field for the DELETE method.

        Returns:
        - str: An HTML string for a hidden input element for the DELETE method.
        """
        return self._input_html("delete")
