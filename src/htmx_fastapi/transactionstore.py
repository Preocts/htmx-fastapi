"""SQLLite3 database interface for the Transaction tables."""

from __future__ import annotations

import sqlite3
from contextlib import closing

from .transaction import Transaction


class TransactionStore:
    """Interface to the Transaction table in the database."""

    def __init__(self, database: sqlite3.Connection) -> None:
        """Initialize the database interface."""
        self.database = database

        self._create_tables()

    def _create_tables(self) -> None:
        """Create the tables in the database."""
        self.database.execute(
            """CREATE TABLE IF NOT EXISTS transactions (
                tid INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT,
                description TEXT,
                amount INTEGER
            )"""
        )

    def add(self, transaction: Transaction) -> None:
        """Add a transaction to the database."""
        self.add_batch([transaction])

    def add_batch(self, transactions: list[Transaction]) -> None:
        """Add a batch of transactions to the database."""
        with closing(self.database.cursor()) as cursor:
            cursor.executemany(
                """
                INSERT INTO transactions (
                    date,
                    description,
                    amount
                )
                VALUES (?, ?, ?)""",
                [
                    (transaction.date, transaction.description, transaction.amount)
                    for transaction in transactions
                ],
            )
            self.database.commit()

    def get(self, date_since: str, date_until: str) -> list[Transaction]:
        """
        Get transactions in the database.

        Args:
            date_since: The start date as a string in YYYY-MM-DD format
            date_until: The end date as a string in YYYY-MM-DD format
        """
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    tid,
                    amount,
                    description,
                    date
                FROM transactions
                WHERE date >= ? AND date <= ?
                ORDER BY date DESC
                """,
                (date_since, date_until),
            )
            return [
                Transaction(
                    tid=row[0],
                    amount=row[1],
                    description=row[2],
                    date=row[3],
                )
                for row in cursor.fetchall()
            ]

    def get_total(self, date_since: str, date_until: str) -> int:
        """
        Get the total amount of transactions in the database.

        Args:
            date_since: The start date as a string in YYYY-MM-DD format
            date_until: The end date as a string in YYYY-MM-DD format
        """
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    SUM(amount)
                FROM transactions
                WHERE date >= ? AND date <= ?
                """,
                (date_since, date_until),
            )
            return cursor.fetchone()[0]

    def get_count(self, date_since: str, date_until: str) -> int:
        """
        Get the number of transactions in the database.

        Args:
            date_since: The start date as a string in YYYY-MM-DD format
            date_until: The end date as a string in YYYY-MM-DD format
        """
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(amount)
                FROM transactions
                WHERE date >= ? AND date <= ?
                """,
                (date_since, date_until),
            )
            return cursor.fetchone()[0]

    def get_count_all(self) -> int:
        """
        Get the number of transactions in the database.
        """
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(amount)
                FROM transactions
                """,
            )
            return cursor.fetchone()[0]

    def get_by_id(self, transaction_id: int) -> Transaction:
        """Get a transaction by its ID."""
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    tid,
                    amount,
                    description,
                    date
                FROM transactions
                WHERE tid = ?
                """,
                (transaction_id,),
            )
            row = cursor.fetchone()
            return Transaction(
                tid=row[0],
                amount=row[1],
                description=row[2],
                date=row[3],
            )

    def update(self, transaction: Transaction) -> None:
        """Update a transaction in the database."""
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                UPDATE transactions
                SET
                    date = ?,
                    description = ?,
                    amount = ?
                WHERE tid = ?
                """,
                (
                    transaction.date,
                    transaction.description,
                    transaction.amount,
                    transaction.tid,
                ),
            )
            self.database.commit()

    def delete(self, transaction_id: int) -> None:
        """Delete a transaction from the database."""
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                DELETE FROM transactions
                WHERE tid = ?
                """,
                (transaction_id,),
            )
            self.database.commit()
