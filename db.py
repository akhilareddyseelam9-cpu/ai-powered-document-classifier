import sqlite3


def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
        c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (username, password))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def check_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    data = c.fetchone()

    conn.close()
    return data


def reset_password(username, new_password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    if user:
        c.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False