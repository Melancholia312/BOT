from db.connection import get_connect


def choose_enemy(user_id, enemy_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET enemy_id={enemy_id} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def find_enemy(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            try_to_find = cursor.execute(f"SELECT user_id FROM users "
                                         f"WHERE enemy_id={user_id} ")

            if try_to_find:
                enemy_id = cursor.fetchone()['user_id']
                return enemy_id
            else:
                return None
    finally:
        connect.close()


def drop_enemy_id(user_id, enemy_id=None):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if enemy_id:
                cursor.execute(f"UPDATE users SET enemy_id=0 "
                               f"WHERE user_id={enemy_id}")
            cursor.execute(f"UPDATE users SET enemy_id=0 "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def check_enemy_id(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT enemy_id FROM users "
                           f"WHERE user_id={user_id} ")
            enemy_id = cursor.fetchone()['enemy_id']
            if enemy_id != 0:
                return True
            else:
                return False

    finally:
        connect.close()


def set_pvp_count(user_id_1, user_id_2, who_winner):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT victory_count, defeat_count FROM users "
                           f"WHERE user_id={user_id_1} ")
            pvp_info_1 = cursor.fetchone()
            cursor.execute(f"SELECT victory_count, defeat_count FROM users "
                           f"WHERE user_id={user_id_2} ")
            pvp_info_2 = cursor.fetchone()
            if who_winner == 1:
                victory_count_1 = pvp_info_1['victory_count'] + 1
                defeat_count_2 = pvp_info_2['defeat_count'] + 1
                cursor.execute(f"UPDATE users SET victory_count={victory_count_1} "
                               f"WHERE user_id={user_id_1}")
                cursor.execute(f"UPDATE users SET defeat_count={defeat_count_2} "
                               f"WHERE user_id={user_id_2} ")
            elif who_winner == 2:
                victory_count_2 = pvp_info_2['victory_count'] + 1
                defeat_count_1 = pvp_info_1['defeat_count'] + 1
                cursor.execute(f"UPDATE users SET victory_count={victory_count_2} "
                               f"WHERE user_id={user_id_2} ")
                cursor.execute(f"UPDATE users SET defeat_count={defeat_count_1} "
                               f"WHERE user_id={user_id_1} ")

            connect.commit()
    finally:
        connect.close()


def is_alive(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT is_dead FROM users "
                           f"WHERE user_id={user_id} ")
            is_dead = cursor.fetchone()['is_dead']
            if is_dead == 0:
                return True
            else:
                return False

    finally:
        connect.close()


def kill_or_heal_hero(user_id, kill):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if kill:
                cursor.execute(f"UPDATE users SET is_dead=1 "
                               f"WHERE user_id={user_id} ")
            else:
                cursor.execute(f"UPDATE users SET is_dead=0 "
                               f"WHERE user_id={user_id} ")
            connect.commit()
    finally:
        connect.close()
