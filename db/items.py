from db.connection import get_connect
dict_with_slots = {'Оружие': 'weapon', 'Голова': 'item_head', 'Тело': 'item_body',
                   'Ноги': 'item_legs', 'Артефакт': 'item_artifact'}


def get_single_item_stat_by_name(name_of_item):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT * FROM items WHERE name="{name_of_item.title()}" ')
            item_info = cursor.fetchone()
            return item_info
    finally:
        connect.close()


def equip_item(user_id, item_name, equip=True):
    item_name = item_name.title()
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT * '
                           f'FROM items WHERE name="{item_name}"')
            item_stats = cursor.fetchone()
            cursor.execute(f'SELECT * '
                           f'FROM users WHERE user_id={user_id}')
            hero_stats = cursor.fetchone()
            cursor.execute(f'SELECT * '
                           f'FROM relation_items_users WHERE user_id={user_id} AND item_id={item_stats["id"]} ')
            relation = cursor.fetchone()
            if equip:
                if hero_stats[dict_with_slots[item_stats['slot']]] == 0:
                    new_ATK = item_stats['ATK'] + hero_stats['ATK']
                    new_HP = item_stats['HP'] + hero_stats['HP']
                    new_MP = item_stats['MP'] + hero_stats['MP']
                    new_strength = item_stats['strength'] + hero_stats['strength']
                    new_agility = item_stats['agility'] + hero_stats['agility']
                    new_intellect = item_stats['intellect'] + hero_stats['intellect']
                    new_luck = item_stats['luck'] + hero_stats['luck']
                    cursor.execute(f"UPDATE users SET {dict_with_slots[item_stats['slot']]}={relation['id']} "
                                   f"WHERE user_id={user_id}")

            else:
                if hero_stats[dict_with_slots[item_stats['slot']]] != 0:
                    new_ATK = hero_stats['ATK'] - item_stats['ATK']
                    new_HP = hero_stats['HP'] - item_stats['HP']
                    new_MP = hero_stats['MP'] - item_stats['MP']
                    new_strength = hero_stats['strength'] - item_stats['strength']
                    new_agility = hero_stats['agility'] - item_stats['agility']
                    new_intellect = hero_stats['intellect'] - item_stats['intellect']
                    new_luck = hero_stats['luck'] - item_stats['luck']
                    cursor.execute(f"UPDATE users SET {dict_with_slots[item_stats['slot']]}=0 "
                                   f"WHERE user_id={user_id}")
            cursor.execute(f"UPDATE users SET ATK={new_ATK}, HP={new_HP}, MP={new_MP}, strength={new_strength}, agility={new_agility}, intellect={new_intellect}, luck={new_luck} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def already_equip_or_not(user_id, item_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT slot '
                           f'FROM items WHERE name="{item_name}"')
            item_slot = dict_with_slots[cursor.fetchone()['slot']]
            cursor.execute(f'SELECT {item_slot} '
                           f'FROM users WHERE user_id={user_id}')
            user_slot = cursor.fetchone()[item_slot]
            if user_slot == 0:
                return True
            return False
    finally:
        connect.close()


def get_weapon_by_relation(relation_id, name=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if name:
                cursor.execute(f"SELECT name FROM relation_items_users "
                               f"INNER JOIN items ON relation_items_users.item_id=items.id "
                               f"WHERE relation_items_users.id={relation_id}")

                weapon_name = cursor.fetchone()
                if weapon_name:
                    return weapon_name['name'].lower()

            else:
                cursor.execute(f"SELECT * FROM relation_items_users "
                               f"INNER JOIN items ON relation_items_users.item_id=items.id "
                               f"WHERE relation_items_users.id={relation_id}")
                weapon_stats = cursor.fetchone()
                return weapon_stats

    finally:
        connect.close()


def check_item_class(user_id, item_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT class FROM users "
                           f"WHERE user_id={user_id}")
            hero_class = cursor.fetchone()['class']
            cursor.execute(f"SELECT class FROM items "
                           f"WHERE name='{item_name}' ")
            item_class = cursor.fetchone()['class']
            if item_class == hero_class:
                return True
            return False
    finally:
        connect.close()


def get_item_class(item_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute('SELECT class FROM items '
                           f'WHERE name="{item_name}" ')
            item_class = cursor.fetchone()['class']
            cursor.execute(f"SELECT name FROM classes "
                           f"WHERE id={item_class}")
            class_name = cursor.fetchone()['name']
            return class_name

    finally:
        connect.close()


def get_all_items():
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute('SELECT name FROM items')
            items = cursor.fetchall()
            return items
    finally:
        connect.close()


def drop_item(user_id, item_name):
    item_name = item_name.title()
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT id, slot '
                           f'FROM items WHERE name="{item_name}"')
            item_info = cursor.fetchone()
            item_id = item_info['id']
            item_slot = dict_with_slots[item_info['slot']]
            cursor.execute(f'SELECT id FROM `relation_items_users` '
                           f'WHERE user_id={user_id} AND item_id={item_id} ')
            relation_id = cursor.fetchall()
            if len(relation_id) > 1:
                relation_id = relation_id[-1]['id']
            else:
                relation_id = relation_id[0]['id']

            cursor.execute(f'SELECT {item_slot} '
                           f'FROM users WHERE user_id={user_id}')
            hero_item_slot_id = cursor.fetchone()[item_slot]
            if relation_id == hero_item_slot_id:
                return False
            else:
                cursor.execute(f'DELETE FROM relation_items_users '
                               f'WHERE user_id={user_id} AND id={relation_id} LIMIT 1 ')
                connect.commit()
                return True
    finally:
        connect.close()
