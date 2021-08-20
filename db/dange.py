from db.connection import get_connect
import random


def enter_dange(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'UPDATE users SET current_dange_floor=1 WHERE user_id={user_id}')
            connect.commit()

    finally:
        connect.close()


def check_dange_floor(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT current_dange_floor FROM users WHERE user_id={user_id}')
            result = cursor.fetchone()
            return result['current_dange_floor']

    finally:
        connect.close()


def check_dange_goal(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT dange_goal FROM users WHERE user_id={user_id}')
        result = cursor.fetchone()
        return result['dange_goal']

    finally:
        connect.close()


def next_stage(user_id):
        connect = get_connect()
        try:
            with connect.cursor() as cursor:
                floor = check_dange_floor(user_id) + 1
                cursor.execute(f'UPDATE users SET current_dange_floor={floor} WHERE user_id={user_id}')
                connect.commit()

        finally:
            connect.close()


def exit_dange(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'UPDATE users SET current_dange_floor=0 WHERE user_id={user_id}')
            connect.commit()

    finally:
        connect.close()


def get_dangeon_mobs(monster_name=None, for_dange=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if for_dange:
                cursor.execute(f"SELECT * FROM monsters WHERE in_dange=1 ")
                monsters = cursor.fetchall()
                return monsters
            else:
                cursor.execute(f"SELECT * FROM monsters "
                               f"WHERE name='{monster_name}' AND in_dange=1 ")
                monster = cursor.fetchone()
                return monster
    finally:
        connect.close()


def give_dange_item(user_id, dange_floor):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT luck FROM users WHERE user_id={user_id} ")
            user_luck = cursor.fetchone()['luck']
            chance = random.randint(1, 100)
            if dange_floor in [5,10]:
                if chance < 40 + user_luck*2:
                    treausre_tier = 1
                else:
                    treausre_tier = 2

            elif dange_floor == 15:
                if chance < 70 - user_luck*3:
                    treausre_tier = 4
                else:
                    treausre_tier = 3

            elif dange_floor == 20:
                if chance < 90-user_luck*2:
                    treausre_tier = 6
                else:
                    treausre_tier = 7

            elif dange_floor == 25:
                if chance < 50-user_luck*2:
                    treausre_tier = 3
                else:
                    treausre_tier = 7

            treasure = f'treasure_{treausre_tier}'
            cursor.execute(f'SELECT {treasure} FROM users WHERE user_id={user_id}')
            treasure_quantity = cursor.fetchone()[treasure]
            cursor.execute(f'UPDATE users SET {treasure}={treasure_quantity} '
                           f'WHERE user_id={user_id}')
            connect.commit()
            treasures_numbers = {'1': 'дорожный сундук',
                                 '2': 'зачарованный сундук',
                                 '3': 'аукционный сундук',
                                 '4': 'потерянная шкатулка',
                                 '5': 'бутылка с письмом',
                                 '6': 'мяукающий мешок',
                                 '7': 'ящик пандоры'}
            return treasures_numbers[str(treausre_tier)].title()
    finally:
        connect.close()


def change_dange_floor(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT current_dange_floor FROM users "
                           f"WHERE user_id={user_id} ")
            current_dange_floor = cursor.fetchone()['current_dange_floor']
            floors = random.randint(1, 3)
            current_dange_floor -= floors
            cursor.execute(f"UPDATE users SET current_dange_floor={current_dange_floor} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def set_busy(user_id, busy):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if busy:
                cursor.execute(f"UPDATE users SET dange_busy={1} "
                               f"WHERE user_id={user_id}")
                connect.commit()
            else:
                cursor.execute(f"UPDATE users SET dange_busy={0} "
                               f"WHERE user_id={user_id}")
                connect.commit()
    finally:
        connect.close()


def check_busy(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT dange_busy FROM users "
                           f"WHERE user_id={user_id} ")
            return cursor.fetchone()['dange_busy']
    finally:
        connect.close()
