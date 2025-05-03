import sqlite3

from payment import Payment

class DatabaseConnection:
    def __init__(self, db_path):
        """
        Initialize the DatabaseConnection with the path to the SQLite database file.
        Establish a connection to the database.
        """
        self.db_path = db_path
        self.connection = None
        self.connect()

    def connect(self):
        """Establish a connection to the SQLite database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print(f"Connected to database at {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        """Close the connection to the SQLite database."""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def setup(self):
        """Create necessary tables in the database if they do not exist."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payment (
                    uuid TEXT UNIQUE NOT NULL,
                    text TEXT NOT NULL,
                    payed_at TIMESTAMP DEFAULT NULL
                )
            """)
            self.connection.commit()
            print("Database tables are set up.")
        except sqlite3.Error as e:
            print(f"Error setting up database tables: {e}")
            raise

    def add_payment_holder(self, payment: Payment):
        """
        Add a payment holder to the database.
        :param uuid: Unique identifier for the payment holder.
        :param text: Text associated with the payment holder.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO payment (uuid, text)
                VALUES (?, ?)
            """, (payment.uid, payment.text))
            self.connection.commit()
            print(f"Payment holder {payment.uid} added.")
        except sqlite3.Error as e:
            print(f"Error adding payment holder: {e}")
            raise

    def mark_payment_as_payed(self, uuid: str):
        """
        Mark a payment as payed by setting the payed_at field to the current time.
        :param uuid: Unique identifier for the payment.
        :return: The text associated with the payment.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                UPDATE payment
                SET payed_at = CURRENT_TIMESTAMP
                WHERE uuid = ?
            """, (uuid,))
            if cursor.rowcount == 0:
                raise ValueError(f"No payment found with uuid: {uuid}")
            cursor.execute("""
                SELECT text FROM payment
                WHERE uuid = ?
            """, (uuid,))
            result = cursor.fetchone()
            self.connection.commit()
            print(f"Payment {uuid} marked as payed.")
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Error marking payment as payed: {e}")
            raise