from __future__ import annotations

import sqlite3

import pytest

from htmx_fastapi.transaction import Transaction
from htmx_fastapi.transactionstore import TransactionStore

MOCK_TRANSACTIONS = [
    (100, "Mock 1", 1234567890),
    (100, "Mock 2", 1234567892),
    (100, "Mock 3", 1234567894),
]


@pytest.fixture
def mock_store() -> TransactionStore:
    """Return a mock TransactionStore."""
    db = sqlite3.connect(":memory:")
    store = TransactionStore(db)
    store.database.executemany(
        """
        INSERT INTO transactions (
            amount,
            description,
            timestamp
        )
        VALUES (?, ?, ?)""",
        MOCK_TRANSACTIONS,
    )
    return store


def test_add_row(mock_store: TransactionStore) -> None:
    transaction = Transaction(
        tid=0,
        amount=100,
        description="Test",
        timestamp=1234567890,
    )

    mock_store.add(transaction)

    cursor = mock_store.database.execute("SELECT * FROM transactions WHERE tid = 4")
    row = cursor.fetchone()

    assert row == (4, 1234567890, "Test", 100)


def test_get_rows(mock_store: TransactionStore) -> None:
    full_result = mock_store.get(1234567890, 1234567894)
    partial_result = mock_store.get(1234567890, 1234567892)

    assert len(full_result) == len(MOCK_TRANSACTIONS)
    assert len(partial_result) == len(MOCK_TRANSACTIONS) - 1


def test_update_row(mock_store: TransactionStore) -> None:
    transaction = Transaction(
        tid=1,
        amount=42069,
        description="Hello there",
        timestamp=1234567900,
    )

    mock_store.update(transaction)

    cursor = mock_store.database.execute(
        "SELECT amount FROM transactions WHERE tid = 1"
    )
    row = cursor.fetchone()

    assert row[0] == 42069


def test_delete_row(mock_store: TransactionStore) -> None:
    mock_store.delete(1)

    cursor = mock_store.database.execute("SELECT * FROM transactions WHERE tid = 1")
    row = cursor.fetchone()

    assert row is None


def test_get_by_id(mock_store: TransactionStore) -> None:
    transaction = mock_store.get_by_id(1)

    assert transaction.tid == 1
    assert transaction.amount == 100
    assert transaction.description == "Mock 1"
    assert transaction.timestamp == 1234567890
