from db.connection import get_connect


def is_admin(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT is_admin FROM users "
                           f"WHERE user_id={user_id}")
            admin = cursor.fetchone()['is_admin']
            if admin == 1:
                return True
            else:
                return False
    finally:
        connect.close()