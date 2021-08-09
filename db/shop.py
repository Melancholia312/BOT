from db.connection import get_connect
import random
from datetime import datetime
dict_with_slots = {'Оружие': 'weapon', 'Голова': 'item_head', 'Тело': 'item_body',
                   'Ноги': 'item_legs', 'Артефакт': 'item_artifact'}


def create_personal_shop(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT class FROM users "
                           f"WHERE user_id={user_id} ")
            hero_class = cursor.fetchone()['class']
            cursor.execute(f"SELECT * FROM shop "
                           f"INNER JOIN items ON shop.item_id=items.id WHERE class={hero_class} ")
            items = cursor.fetchall()

            cursor.execute(f"SELECT * FROM user_shop "
                           f"WHERE user_id={user_id} ")
            user_items_now = cursor.fetchall()

            random.shuffle(items)
            user_items = items[:6]
            if not user_items_now:
                for item in user_items:
                    cursor.execute(f"INSERT INTO user_shop(user_id, shop_item_id, cost) "
                                   f"VALUES ({user_id}, {item['item_id']}, {item['cost']}) ")
            else:
                cursor.execute(f"DELETE FROM user_shop "
                               f"WHERE user_id={user_id} ")
                for item in user_items:
                    cursor.execute(f"INSERT INTO user_shop(user_id, shop_item_id, cost) "
                                   f"VALUES ({user_id}, {item['item_id']}, {item['cost']}) ")

            connect.commit()
    finally:
        connect.close()


def get_personal_shop_items(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_shop "
                           f"INNER JOIN items ON user_shop.shop_item_id=items.id WHERE user_id={user_id}")
            items = cursor.fetchall()
            return items
    finally:
        connect.close()


def get_time_to_recreate_shop(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"SELECT time_to_recreate_shop FROM users "
                           f"WHERE user_id={user_id}")
            time_from_db = cursor.fetchone()['time_to_recreate_shop']

            if time_from_db != None:
                delta = datetime.now() - time_from_db
                if delta.days >= 1:
                    cursor.execute(f"UPDATE users SET time_to_recreate_shop='{now}' "
                                   f"WHERE user_id={user_id} ")
                    connect.commit()
                    return True
                else:
                    return False

            else:
                cursor.execute(f"UPDATE users SET time_to_recreate_shop='{now}' "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return True

    finally:
        connect.close()


def buy_item(user_id, item_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT money FROM users "
                           f"WHERE user_id={user_id} ")
            hero_money = cursor.fetchone()['money']
            cursor.execute(f"SELECT cost FROM shop "
                           f"WHERE item_id={item_id} ")
            item_cost = cursor.fetchone()['cost']
            if item_cost <= hero_money:
                new_hero_money = hero_money - item_cost
                cursor.execute(f"UPDATE users SET money={new_hero_money} "
                               f"WHERE user_id={user_id}")
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {item_id}) ")
                connect.commit()
                return True
            else:
                return False
    finally:
        connect.close()