"""Generate mock data for render testing."""

from __future__ import annotations

import datetime
import pathlib
import random
import re
import sqlite3

from htmx_fastapi.transaction import Transaction
from htmx_fastapi.transactionstore import TransactionStore

WORDS = "Lorem ipsum dolor sit amet ipsum duo et. Kasd dolor et rebum ut dolores molestie praesent ad sed dolor lorem enim nonumy diam consetetur dolor. Dolore duo labore vulputate dolor aliquyam ea kasd tempor nobis et lorem consetetur et voluptua erat et. Dolore dolor duo dolor eum consequat. Dolor vel lorem et ut. Aliquyam labore justo justo ea sed dignissim dolore diam. Tempor magna et no dolor esse duis amet eos. No eu amet dolore minim diam aliquam stet nonumy lobortis. Kasd vel ipsum vero sed at sit amet dolores et sadipscing accusam rebum eleifend dolor facilisis accumsan. Vel ipsum accusam ad labore id ut accusam invidunt sit at. Takimata esse aliquip molestie elitr eum voluptua amet. Quis autem duo sanctus nostrud et et tempor consequat diam stet amet labore te suscipit. Minim vel et. Dolore nonumy eos justo no clita laoreet volutpat lorem sea sadipscing accusam sea invidunt labore dolore accusam consetetur."
TRANSACTIONS_PER_DAY = 10
NUMBER_OF_DAYS = 900


def _split_words(words: str) -> list[str]:
    """Split words into a list."""
    words = re.sub(r"[^\w\s]", "", words)
    return words.split(" ")


def _generate_transactions(dayscount: int) -> list[Transaction]:
    """Generate mock transactions."""
    date_start = datetime.datetime.now() - datetime.timedelta(days=dayscount)

    words = _split_words(WORDS)
    transactions = []

    for day in range(dayscount):
        for _ in range(TRANSACTIONS_PER_DAY):
            transaction = Transaction(
                tid=0,
                amount=random.randint(100, 10000),
                description=" ".join(random.choices(words, k=5)),
                date=date_start.strftime("%Y-%m-%d"),
            )
            transactions.append(transaction)

        date_start += datetime.timedelta(days=1)

    return transactions


if __name__ == "__main__":
    dbfile = pathlib.Path("transactions.db")

    if dbfile.exists():
        dbfile.unlink()

    conn = sqlite3.connect(dbfile)
    store = TransactionStore(conn)

    transactions = _generate_transactions(NUMBER_OF_DAYS)

    store.add_batch(transactions)

    conn.close()

    print(f"generated {len(transactions)} transactions in {dbfile}")
