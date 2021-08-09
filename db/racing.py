from db.connection import get_connect


def get_all_bets(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM racing "
                           f"WHERE peer_id={peer_id}")
            races = cursor.fetchall()
            return races
    finally:
        connect.close()


def make_bet(user_id, bet, peer_id, racer_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM racing "
                           f"WHERE peer_id={peer_id} AND user_id={user_id} ")
            user_bet = cursor.fetchone()
            cursor.execute(f"SELECT money FROM users "
                           f"WHERE user_id={user_id}")
            user_money = cursor.fetchone()['money']

            new_user_money = user_money - bet

            cursor.execute(f"UPDATE users SET money={new_user_money} "
                           f"WHERE user_id={user_id} ")
            connect.commit()

            if user_bet:
                if user_bet['racer_name'] == racer_name:
                    user_bet = user_bet['bet']
                    user_bet += bet
                    cursor.execute(f"UPDATE racing SET bet={user_bet} "
                                   f"WHERE peer_id={peer_id} AND user_id={user_id} ")
                    connect.commit()
                    return f'Вы успешно доставили на {racer_name} {bet} монет!'
                else:
                    return False

            else:
                cursor.execute(f"INSERT INTO racing(user_id, bet, peer_id, racer_name) "
                               f"VALUES ({user_id}, {bet}, {peer_id}, '{racer_name}') ")
                connect.commit()
                return f'Вы успешно поставили на {racer_name} {bet} монет!'



    finally:
        connect.close()


def delete_all_bets(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"DELETE FROM racing "
                           f"WHERE peer_id={peer_id}")
            connect.commit()
    finally:
        connect.close()


def get_big_bet(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT bet FROM racing "
                           f"WHERE peer_id={peer_id} ORDER BY -bet LIMIT 1 ")
            max_bet = cursor.fetchone()
            if max_bet:
                return max_bet['bet']/2
            else:
                return 0
    finally:
        connect.close()

