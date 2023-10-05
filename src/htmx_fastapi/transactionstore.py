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
                timestamp INTEGER,
                description TEXT,
                amount INTEGER
            )"""
        )

    def add(self, transaction: Transaction) -> None:
        """Add a transaction to the database."""
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                INSERT INTO transactions (
                    timestamp,
                    description,
                    amount
                )
                VALUES (?, ?, ?)""",
                (transaction.timestamp, transaction.description, transaction.amount),
            )
            self.database.commit()

    def get(self, since: int, until: int) -> list[Transaction]:
        """
        Get transactions in the database.

        Args:
            since: The earliest timestamp to return.
            until: The latest timestamp to return.
        """
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                SELECT
                    tid,
                    amount,
                    description,
                    timestamp
                FROM transactions
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
                """,
                (since, until),
            )
            return [
                Transaction(
                    tid=row[0],
                    amount=row[1],
                    description=row[2],
                    timestamp=row[3],
                )
                for row in cursor.fetchall()
            ]

    def update(self, transaction: Transaction) -> None:
        """Update a transaction in the database."""
        with closing(self.database.cursor()) as cursor:
            cursor.execute(
                """
                UPDATE transactions
                SET
                    timestamp = ?,
                    description = ?,
                    amount = ?
                WHERE tid = ?
                """,
                (
                    transaction.timestamp,
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
