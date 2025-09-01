"""Database module for managing carbon credits and transactions."""

import json
import sqlite3
from typing import List, Dict

from data_models import CreditTransaction


class Database:
    """Class to manage the SQLite database for carbon credits and transactions.
    Attributes:
        db_path (str): Path to the SQLite database file.
    """

    def __init__(self, db_path: str = "ccx_marketplace.db"):
        """Initializes the Database class and sets up the database."""
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initializes the database and creates necessary tables."""
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        self._create_credits_table(cursor)
        self._create_transactions_table(cursor)
        connection.commit()
        connection.close()

    def get_credits(self) -> list[dict]:
        """Fetches all carbon credits from the database.

        Returns:
            credits: List of carbon credit dictionaries.
        """
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM carbon_credits ")
        rows = cursor.fetchall()
        connection.close()
        credits = []
        for row in rows:
            credit = dict(row)
            credit["public_details"] = json.loads(credit["public_details"])
            if credit["private_details"]:
                credit["private_details"] = json.loads(credit["private_details"])
            credits.append(credit)

        return credits

    def get_total_available_amount(self) -> int:
        """Calculates the total available amount of carbon credits.
        Returns:
            total_available: Total quantity of available carbon credits.
        """
        connection = sqlite3.connect(self.db_path)
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SUM(quantity_available) as total_available FROM carbon_credits"
        )
        result = cursor.fetchone()
        connection.close()
        return result[0] if result and result[0] is not None else 0

    def get_credit_by_id(self, credit_id: str) -> dict | None:
        """Fetches a specific carbon credit by its ID.
        Args:
            credit_id (str): The ID of the carbon credit.
        Returns:
            credit: Carbon credit dictionary or None if not found.
        """
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row

        cursor = connection.cursor()
        command = f"SELECT * FROM carbon_credits WHERE id = '{credit_id}'"
        cursor.execute(command)
        row = cursor.fetchone()
        connection.close()
        if row:
            credit = dict(row)
            credit["public_details"] = json.loads(credit["public_details"])
            if credit["private_details"]:
                credit["private_details"] = json.loads(credit["private_details"])
            return credit
        return None

    def purchase_credit(self, transaction: CreditTransaction):
        """Processes a credit purchase transaction.
        Args:
            transaction (CreditTransaction): The transaction details.
        Returns:
            success (bool): True if the transaction was successful, False otherwise.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO transactions 
                (id, credit_id, buyer_id, quantity, price_per_ton, transaction_date, transaction_hash, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    transaction.id,
                    transaction.credit_id,
                    transaction.buyer_id,
                    transaction.quantity,
                    transaction.price_per_ton,
                    transaction.transaction_date,
                    transaction.transaction_hash,
                    transaction.status,
                ),
            )
            # Update credit quantity
            cursor.execute(
                """
                UPDATE carbon_credits 
                SET quantity_available = quantity_available - ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (transaction.quantity, transaction.credit_id),
            )

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Transaction failed: {e}")
            return False
        finally:
            conn.close()

    def get_transactions(self, buyer_id: str = None) -> List[Dict]:
        """Get transactions, optionally filtered by buyer.
        Args:
            buyer_id (str, optional): The ID of the buyer to filter transactions. Defaults to None.
        Returns:
            List[Dict]: List of transaction dictionaries.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if buyer_id:
            cursor.execute("SELECT * FROM transactions WHERE buyer_id = ?", (buyer_id,))
        else:
            cursor.execute("SELECT * FROM transactions")

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def _create_credits_table(self, cursor: sqlite3.Cursor):
        """Creates the carbon_credits table if it doesn't exist.
        Args:
            cursor (sqlite3.Cursor): SQLite cursor object.
        """
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS carbon_credits (
                id TEXT PRIMARY KEY,
                project_name TEXT NOT NULL,
                supplier TEXT NOT NULL,
                credit_type TEXT NOT NULL,
                vintage INTEGER NOT NULL,
                quantity_available INTEGER NOT NULL,
                price_per_ton REAL NOT NULL,
                location TEXT NOT NULL,
                verification_status TEXT NOT NULL,
                methodology TEXT NOT NULL,
                public_details TEXT NOT NULL,
                private_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

    def _create_transactions_table(self, cursor: sqlite3.Cursor):
        """Creates the transactions table if it doesn't exist.
        Args:
            cursor (sqlite3.Cursor): SQLite cursor object.
        """

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                credit_id TEXT NOT NULL,
                buyer_id TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price_per_ton REAL NOT NULL,
                transaction_date TIMESTAMP NOT NULL,
                transaction_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (credit_id) REFERENCES carbon_credits (id)
            )
        """
        )


# Initialize database with sample data
def init_sample_data():
    """Initializes the database with sample carbon credit data from a JSON file.
    Returns:
        db (Database): The initialized Database instance.
    """
    db = Database()

    existing_credits = db.get_credits()
    if existing_credits:
        return db

    with open("../resources/sample_credits.json") as json_data:
        sample_credits = json.load(json_data)

    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()

    for credit in sample_credits:
        cursor.execute(
            """
            INSERT INTO carbon_credits 
            (id, project_name, supplier, credit_type, vintage, quantity_available, 
             price_per_ton, location, verification_status, methodology, public_details, private_details)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                credit["id"],
                credit["project_name"],
                credit["supplier"],
                credit["credit_type"],
                credit["vintage"],
                credit["quantity_available"],
                credit["price_per_ton"],
                credit["location"],
                credit["verification_status"],
                credit["methodology"],
                json.dumps(credit["public_details"]),
                json.dumps(credit["private_details"]),
            ),
        )

    conn.commit()
    conn.close()
    return db


if __name__ == "__main__":
    init_sample_data()
