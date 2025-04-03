import sqlite3
from typing import Optional, Union, Dict, Any, List

from .errors import FieldNotFound
from .schema import Schema, as_sql_type


class Collection:
    """
    A class to represent a collection in the database.

    Args:
        name (str): The name of the collection.
        schema (Schema): The schema for the collection.
        connection (sqlite3.Connection): The SQLite database connection.
    """

    def __init__(
        self,
        name: str,
        schema: Schema,
        connection: sqlite3.Connection,
    ):
        """
        Initialize the collection with given name, schema, and connection.

        Args:
            name (str): The name of the table.
            schema (Schema): The schema of the table.
            connection (sqlite3.Connection): The SQLite database connection.

        """
        self.name = name
        self.schema = schema
        self.connection = connection
        self.cursor = connection.cursor()

    def clear(self):
        """
        Removes all records from the collection.
        """
        self.cursor.execute(f"TRUNCATE TABLE {self.name}")
        self.connection.commit()

    def drop(self, confirm: bool = False) -> bool:
        """
        Drops the collection from the database.

        Args:
            confirm (bool): If True, the collection will be dropped. Otherwise, it will not be dropped.
        Returns:
            bool: True if the collection was dropped, False otherwise.
        """
        if not confirm:
            return False
        self.cursor.execute(f"DROP TABLE IF EXISTS {self.name}")
        self.connection.commit()
        return True

    def insert(self, **data):
        """
        Insert a record into the collection.

        Args:
            **data: The data to insert into the collection.
        Returns:
            int: The key of the inserted record.
        """
        if len(data) != len(self.schema.fields):
            raise ValueError("Data length does not match schema fields length.")
        for field in self.schema.fields:
            if field.name not in data:
                raise ValueError(f"Missing field: {field.name}")
            if str(as_sql_type(type(data[field.name]))) != field.sql_type:
                raise TypeError(f"Incorrect type for field: {field.name}")

        columns = ", ".join(data.keys())
        placeholders = ", ".join("?" * len(data))
        values = tuple(data.values())
        sql = f"INSERT INTO {self.name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(sql, values)
        self.connection.commit()
        return self.cursor.lastrowid

    def delete(self, key: Union[int, str]):
        """
        Delete a record by its key.

        Args:
            key (Union[int, str]): The key of the record to delete.
        """
        self.cursor.execute(f"DELETE FROM {self.name} WHERE id = ?", (key,))
        self.connection.commit()

    def remove_field(self, field: str):
        """
        Removes a field from the table.

        Args:
            field (str): The name of the field to remove.
        Raises:
            FieldNotFound: If the field does not exist in the table.
        """
        try:
            self.cursor.execute(f"ALTER TABLE {self.name} DROP COLUMN {field}")
            self.connection.commit()
        except sqlite3.OperationalError as e:
            raise FieldNotFound(f"field '{field}' not found in collection '{self.name}'.") from e

    def fetch(self, key: Union[int, str]) -> Optional[Dict[str, Any]]:
        """
        Fetch all records from the collection.
        """
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE id = ?", (key,))
        data = self.cursor.fetchone()
        if data is None:
            return None
        return dict(zip([column[0] for column in self.cursor.description], data))

    def __iter__(self):
        """
        Iterate over the records in the table.
        """
        self.cursor.execute(f"SELECT * FROM {self.name}")
        for row in self.cursor.fetchall():
            yield dict(zip([column[0] for column in self.cursor.description], row))

    def all(self):
        """
        Fetch all records from the table.
        """
        self.cursor.execute(f"SELECT * FROM {self.name}")
        return [
            dict(zip([column[0] for column in self.cursor.description], row))
            for row in self.cursor.fetchall()
        ]

    def union(self, other: "Collection") -> List[Dict[str, Any]]:
        """
        Fetch all records from two collections.
        """
        self.cursor.execute(f"SELECT * FROM {self.name} UNION SELECT * FROM {other.name}")
        return [
            dict(zip([column[0] for column in self.cursor.description], row))
            for row in self.cursor.fetchall()
        ]

    def join(self, field: str, other: "Collection", on: str) -> List[Dict[str, Any]]:
        """
        Join two collections on a specified field.

        Args:
            field (str): The field to join on in the current collection.
            other (Collection): The other collection to join with.
            on (str): The field to join on in the other collection.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the joined records.
        """
        self.cursor.execute(
            f"SELECT * FROM {self.name} JOIN {other.name} ON {self.name}.{field} = {other.name}.{on}"
        )
        return [
            dict(zip([column[0] for column in self.cursor.description], row))
            for row in self.cursor.fetchall()
        ]

    def distinct(self, field: str) -> List[Any]:
        """
        Fetch distinct values from a field.

        Args:
            field (str): The field to fetch distinct values from.

        Returns:
            List[Any]: A list of distinct values from the specified field.
        """
        self.cursor.execute(f"SELECT DISTINCT {field} FROM {self.name}")
        return [row[0] for row in self.cursor.fetchall()]

    def order_by(self, *fields: str, desc: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch all records ordered by one or more fields.

        Args:
            *fields (str): The fields to order by.
            desc (bool): If True, order in descending order. Default is ascending order.
        """
        order = "DESC" if desc else "ASC"
        if len(fields) == 0:
            raise ValueError("At least one column must be specified.")
        placeholder = ", ".join(fields)
        self.cursor.execute(f"SELECT * FROM {self.name} ORDER BY {placeholder} {order}")
        return [
            dict(zip([column[0] for column in self.cursor.description], row))
            for row in self.cursor.fetchall()
        ]

    def avg(self, field: str) -> float:
        """
        Calculate the average of a numeric column.

        Args:
            field (str): The field to calculate the average for.

        Returns:
            float: The average value of the specified field.
        """
        self.cursor.execute(f"SELECT AVG({field}) FROM {self.name}")
        return self.cursor.fetchone()[0]

    def sum(self, field: str) -> float:
        """
        Calculate the sum of a numeric field.

        Args:
            field (str): The field to calculate the sum for.

        Returns:
            float: The sum of the specified field.
        """
        self.cursor.execute(f"SELECT SUM({field}) FROM {self.name}")
        return self.cursor.fetchone()[0]

    def min(self, field: str) -> Union[int, float]:
        """
        Calculate the minimum of a numeric field.

        Args:
            field (str): The field to calculate the minimum for.

        Returns:
            Union[int, float]: The minimum value of the specified field.
        """
        self.cursor.execute(f"SELECT MIN({field}) FROM {self.name}")
        return self.cursor.fetchone()[0]

    def max(self, field: str) -> Union[int, float]:
        """
        Calculate the maximum of a numeric field.

        Args:
            field (str): The field to calculate the maximum for.
        """
        self.cursor.execute(f"SELECT MAX({field}) FROM {self.name}")
        return self.cursor.fetchone()[0]

    def count(self) -> int:
        """
        Count the number of records in the collection.

        Returns:
            int: The number of records in the collection.
        """
        self.cursor.execute(f"SELECT COUNT(*) FROM {self.name}")
        return self.cursor.fetchone()[0]

    def where(self, *conditions: str) -> List[Dict[str, Any]]:
        """
        Execute a custom database query with conditions.

        Args:
            *conditions (str): The conditions to apply to the query.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries representing the records that match the conditions.
        """
        conditions = ", ".join(conditions)
        self.cursor.execute(f"SELECT * FROM {self.name} WHERE {conditions};")
        return [
            dict(zip([column[0] for column in self.cursor.description], row))
            for row in self.cursor.fetchall()
        ]

    def update(self, key: Union[int, str], **data: Any):
        """
        Update a record by its key.

        Args:
            key (Union[int, str]): The key of the record to update.
            **data: The data to update in the record.
        """
        allowed = [f.name for f in self.schema.fields]
        for k, v in data.items():
            if k not in allowed:
                raise ValueError(f"Invalid field: {k}")
            if as_sql_type(type(v)) != self.schema.resolve_field_type(k):
                raise TypeError(f"Incorrect type for field: {k}")
        placeholders = ", ".join(f"{k} = ?" for k in data.keys())
        values = tuple(data.values()) + (key,)
        sql = f"UPDATE {self.name} SET {placeholders} WHERE id = ?"
        self.cursor.execute(sql, values)
        self.connection.commit()
