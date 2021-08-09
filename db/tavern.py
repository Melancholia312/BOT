from db.connection import get_connect


def get_drinks(by_name=False, name=None):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if not by_name:
                cursor.execute(f"SELECT * FROM drinks")
                drinks = cursor.fetchall()
                return drinks
            else:
                cursor.execute(f"SELECT * FROM drinks WHERE name='{name}' ")
                drink = cursor.fetchone()
                return drink
    finally:
        connect.close()


