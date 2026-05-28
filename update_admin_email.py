import sqlite3


DB_PATH = "instance/crypto_bot.db"
ADMIN_EMAIL = "aldanehutchinson5@gmail.com"


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET email = ? WHERE role = ?",
        (ADMIN_EMAIL, "super_admin"),
    )
    conn.commit()

    if cur.rowcount:
        print(f"Updated {cur.rowcount} super_admin row(s)")
    else:
        print("No rows updated - check DB")

    conn.close()


if __name__ == "__main__":
    main()
