from db.connection import get_connect


def check_invite(referal_key):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT user_id FROM users "
                           f"WHERE referal_key={referal_key} ")
            inviter_id = cursor.fetchone()['user_id']
            return inviter_id
    finally:
        connect.close()


def set_inviter(referal_id, inviter_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"INSERT INTO referals(inviter_id, referal) "
                           f"VALUES({inviter_id}, {referal_id}) ")
            connect.commit()
    finally:
        connect.close()


def set_own_referal_code(user_id, referal_key):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET referal_key={referal_key} "
                           f"WHERE user_id={user_id} ")
            connect.commit()
    finally:
        connect.close()


def already_referal_or_not(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            res = cursor.execute(f"SELECT * FROM referals "
                                 f"WHERE referal={user_id} ")
            if res == 1:
                return True
            else:
                return False

    finally:
        connect.close()


def get_user_referal_key(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT referal_key FROM users "
                           f"WHERE user_id={user_id} ")
            referal_key = cursor.fetchone()['referal_key']
            return referal_key
    finally:
        connect.close()


def count_referals(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM referals "
                           f"WHERE inviter_id={user_id} ")
            referals = cursor.fetchall()
            return len(referals)

    finally:
        connect.close()
