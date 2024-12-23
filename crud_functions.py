import sqlite3

def connect_db():
    connection = sqlite3.connect("u_14_4_BD_for_telegram.db")
    cursor = connection.cursor()
    return connection, cursor

def disconnect_db(connection):
    connection.commit()
    connection.close()

def initiate_db():
    connection, cursor = connect_db()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Products(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    price INTEGER NOT NULL
    )
    ''')
    for i in range(1, 5):
        cursor.execute("INSERT INTO Products (title, description, price) VALUES (?, ?, ?)", (f"Product{i}",
                                                                                               f"about_example{i}",
                                                                                               f"{i * 10}"))
    disconnect_db(connection)


def get_all_products():
    connection, cursor = connect_db()
    cursor.execute("SELECT title, description, price FROM Products")
    result = cursor.fetchall()
    disconnect_db(connection)
    return result

# initiate_db()
# print(get_all_products())

