import sqlite3

con = sqlite3.connect("Users.sqlite")
cursor = con.cursor()

# query = """ Create table Users (
#     id integer PRIMARY KEY AUTOINCREMENT,
#     username text NOT NULL,
#     password text NOT NULL,
#     email text NOT NULL,
#     address text NOT NULL,
#     phone text NOT NULL
# )
# """

query = """ Create table Houses (
    id integer PRIMARY KEY AUTOINCREMENT,
    username text NOT NULL,
    house_name text NOT NULL,
    structure_type text NOT NULL,
    sensor_type text NOT NULL,
    sensor_ui_value text
)
"""

# query = "DROP TABLE Houses;"
cursor.execute(query)


def main():
    pass


if __name__ == '__main__':
    main()
