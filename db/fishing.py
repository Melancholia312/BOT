from db.connection import get_connect
from datetime import datetime
import random


def get_fishing_info(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT fish_rod, fish_time, fish_count FROM users "
                           f"WHERE user_id={user_id}")
            fishing_info = cursor.fetchone()
            return fishing_info
    finally:
        connect.close()


def buy_fish_rod(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT fish_rod, money FROM users "
                           f"WHERE user_id={user_id}")
            user_info = cursor.fetchone()
            user_money = user_info['money'] - 260
            user_rod = user_info['fish_rod']
            if user_rod == 0:
                cursor.execute(f"UPDATE users SET fish_rod={1}, money={user_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return True
            else:
                return False
    finally:
        connect.close()


def check_fish_try(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT fish_count FROM users "
                           f"WHERE user_id={user_id}")
            fish_info = cursor.fetchone()['fish_count']
            if fish_info > 0:
                return True
            else:
                return False
    finally:
        connect.close()


def reset_fish_time(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"SELECT fish_time FROM users "
                           f"WHERE user_id={user_id}")
            time_from_db = cursor.fetchone()['fish_time']

            if time_from_db != None:
                delta = datetime.now() - time_from_db
                if delta.days >= 1:
                    cursor.execute(f"UPDATE users SET fish_time='{now}', fish_count={3} "
                                   f"WHERE user_id={user_id} ")
                    connect.commit()
            else:
                cursor.execute(f"UPDATE users SET fish_time='{now}', fish_count={3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()

    finally:
        connect.close()


def give_item(user_id, item_tier):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT id, name FROM items "
                           f"WHERE tier={item_tier}")
            items = cursor.fetchall()
            user_item = random.choice(items)
            cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                           f"VALUES ({user_id}, {user_item['id']}) ")
            connect.commit()
            return user_item['name']
    finally:
        connect.close()


def brake_rode(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET fish_rod={0} "
                           f"WHERE user_id={user_id}")
            connect.commit()

    finally:
        connect.close()


def spend_fish_count(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT fish_count FROM users "
                           f"WHERE user_id={user_id}")
            fish_count = cursor.fetchone()['fish_count']-1
            cursor.execute(f"UPDATE users SET fish_count={fish_count} "
                           f"WHERE user_id={user_id}")
            connect.commit()

    finally:
        connect.close()
