from .typeconverter import AsType


class Field:
    """
    A class representing a field in the database schema.
    """

    def __init__(
        self,
        name: str,
        dtype: AsType,
        *constraints: str,
    ):
        """
        Initializes a Field instance.

        Args:
            name (str): The name of the field.
            dtype (AsType): The data type of the field.
        """
        self.name = name
        self.sql_type = str(dtype)
        self.constraints = list(constraints)


class Schema:
    """
    A class representing the schema of a database.
    """

    def __init__(self, table_name: str, *fields: Field):
        """
        Initializes a Schema instance.

        Args:
            table_name (str): The name of the table.
        """
        self.table_name = table_name
        self.fields = list(fields)

    def add_field(self, field: Field):
        """
        Adds a fields to the schema.
        Args:
            field (Field): The field to add to the schema.
        """
        self.fields.append(field)