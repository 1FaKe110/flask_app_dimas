import sqlite3

con = sqlite3.connect("Users.sqlite")
cursor = con.cursor()

query = """ Create table Users (
    id integer PRIMARY KEY AUTOINCREMENT,
    username text NOT NULL,
    password text NOT NULL,
    email text NOT NULL,
    address text NOT NULL,
    phone text NOT NULL
)
"""
cursor.execute(query)



def main():
    pass


if __name__ == '__main__':
    main()
