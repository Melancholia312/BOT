import datetime

from db.connection import get_connect
dict_with_slots = {'Оружие': 'weapon', 'Голова': 'item_head', 'Тело': 'item_body',
                   'Ноги': 'item_legs', 'Артефакт': 'item_artifact'}


def get_hero_info(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT user_id, name, money, class, subclass, lvl, is_dead, energy, max_energy, weapon, '
                           f'item_head, item_body, item_legs, item_artifact, exp, max_exp, image, luck '
                           f'FROM users WHERE user_id={user_id}')
            hero = cursor.fetchone()
            return hero
    finally:
        connect.close()


def get_stats(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT name, lvl, subclass, is_dead, class, MP, HP, ATK, strength, agility, '
                           f'intellect, CRIT_RATE, luck FROM users WHERE user_id={user_id}')
            hero_stats = cursor.fetchone()
            return hero_stats
    finally:
        connect.close()


def get_stat_multiply(hero_class):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT multiply_strength_atk, '
                           f'multiply_agility_atk, '
                           f'multiply_intellect_atk, '
                           f'multiply_strength_hp, '
                           f'multiply_agility_hp, '
                           f'multiply_intellect_hp, '
                           f'multiply_strength_mp, '
                           f'multiply_agility_mp, '
                           f'multiply_intellect_mp '
                           f'FROM classes WHERE id={hero_class}')
            class_multiply = cursor.fetchone()
            return class_multiply
    finally:
        connect.close()


def get_user_inventory(user_id, all_info=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if all_info:
                cursor.execute(f"SELECT * FROM relation_items_users "
                               f"INNER JOIN items ON relation_items_users.item_id=items.id "
                               f"WHERE relation_items_users.user_id={user_id}")
                hero_items = cursor.fetchall()
                return hero_items
            else:
                cursor.execute(f"SELECT name, tier, slot, class FROM relation_items_users "
                               f"INNER JOIN items ON relation_items_users.item_id=items.id "
                               f"WHERE relation_items_users.user_id={user_id}")
                hero_items_only_with_small_description = cursor.fetchall()
                return hero_items_only_with_small_description
    finally:
        connect.close()


def get_upgrade_points(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT upgrade_points '
                           f'FROM users WHERE user_id={user_id}')
            hero_points = cursor.fetchone()
            return hero_points['upgrade_points']
    finally:
        connect.close()


def add_stat_point(user_id, name_of_stat):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT {name_of_stat}, upgrade_points '
                           f'FROM users WHERE user_id={user_id}')
            info = cursor.fetchone()
            stat = info[name_of_stat]
            new_upgrade_points = info['upgrade_points'] - 1
            add_point_to_stat = stat + 1
            cursor.execute(f"UPDATE users SET {name_of_stat}={add_point_to_stat}, upgrade_points={new_upgrade_points} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def check_full_inventory(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT max_items FROM users "
                           f"WHERE user_id={user_id} ")
            max_items = cursor.fetchone()['max_items']
            cursor.execute(f"SELECT item_id FROM relation_items_users "
                           f"WHERE user_id={user_id} ")
            user_items = cursor.fetchall()
            if len(user_items) < max_items:
                return True
            return False
    finally:
        connect.close()


def check_pvp_stat(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT victory_count, defeat_count, enemy_id FROM users "
                           f"WHERE user_id={user_id} ")
            pvp_info = cursor.fetchone()
            try_to_find = cursor.execute(f"SELECT user_id FROM users "
                                         f"WHERE enemy_id={user_id} ")

            if try_to_find:
                pvp_info['have_pvp_offer'] = True
                pvp_info['enemy_id'] = cursor.fetchone()['user_id']
            else:
                pvp_info['have_pvp_offer'] = False
            return pvp_info
    finally:
        connect.close()


def get_top_user_by_victory_count():
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT user_id, name, victory_count FROM users "
                           f"ORDER BY -victory_count LIMIT 10")
            top_list_victory_count = cursor.fetchall()
            return top_list_victory_count
    finally:
        connect.close()


def get_top_user_by_money():
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT user_id, name, money FROM users "
                           f"ORDER BY -money LIMIT 10")
            top_list_money = cursor.fetchall()
            return top_list_money
    finally:
        connect.close()


def get_top_user_by_lvl():
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT user_id, name, lvl FROM users "
                           f"ORDER BY -lvl LIMIT 10")
            top_list_lvl = cursor.fetchall()
            return top_list_lvl
    finally:
        connect.close()


def add_money(user_id, money, with_mul=False):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if with_mul:
                cursor.execute(f"SELECT money, money_multiply FROM users "
                               f"WHERE user_id={user_id}")
                user_money_info = cursor.fetchone()
                money_multiply = user_money_info['money_multiply']
                user_money = user_money_info['money']
                if money > 0:
                    user_money = user_money+money*money_multiply
                else:
                    user_money = user_money+money
                cursor.execute(f"UPDATE users SET money={user_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return money*money_multiply
            else:
                cursor.execute(f"SELECT money FROM users "
                               f"WHERE user_id={user_id}")
                user_money_info = cursor.fetchone()
                user_money = user_money_info['money']
                user_money = user_money + money
                cursor.execute(f"UPDATE users SET money={user_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return money
    finally:
        connect.close()


def check_energy(user_id, need_energy):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT energy FROM users "
                           f"WHERE user_id={user_id}")
            user_energy = cursor.fetchone()['energy']
            if user_energy >= need_energy:
                cursor.execute(f"UPDATE users SET energy={user_energy - need_energy} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return True
            else:
                return False

    finally:
        connect.close()


def go_to_sleep(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.datetime.now()
            end_sleep_time = now + datetime.timedelta(hours=3)
            end_sleep_time = end_sleep_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE users SET sleep_time='{end_sleep_time}', is_sleeping=1 "
                           f"WHERE user_id={user_id}")
            connect.commit()

    finally:
        connect.close()


def wake_up(user_id, rest=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if rest:
                cursor.execute(f"SELECT max_energy FROM users "
                               f"WHERE user_id={user_id}")
                max_energy = cursor.fetchone()['max_energy']
                cursor.execute(f"UPDATE users SET sleep_time=NULL, energy={max_energy}, is_sleeping=0, is_dead=0 "
                               f"WHERE user_id={user_id} ")
            else:
                cursor.execute(f"UPDATE users SET sleep_time=NULL, is_sleeping=0 "
                               f"WHERE user_id={user_id} ")
            connect.commit()

    finally:
        connect.close()


def check_sleep(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT is_sleeping FROM users "
                           f"WHERE user_id={user_id}")
            is_sleeping = cursor.fetchone()['is_sleeping']

            if is_sleeping == 1:
                return True
            else:
                return False


    finally:
        connect.close()


def get_user_status(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT is_sleeping, sleep_time, is_dead, energy, max_energy, "
                           f"in_expedition, expedition_time, on_job, end_job, job_id FROM users "
                           f"WHERE user_id={user_id}")
            hero_status = cursor.fetchone()
            return hero_status
    finally:
        connect.close()


def send_money(user_id, recipient, value):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT money FROM users "
                           f"WHERE user_id={user_id}")
            sender_money = cursor.fetchone()['money']
            cursor.execute(f"SELECT money FROM users "
                           f"WHERE user_id={recipient}")
            recipient_money = cursor.fetchone()['money']

            new_sender_money = sender_money - value
            new_recipient_money = recipient_money + value

            cursor.execute(f"UPDATE users SET money={new_sender_money} "
                           f"WHERE user_id={user_id} ")
            cursor.execute(f"UPDATE users SET money={new_recipient_money} "
                           f"WHERE user_id={recipient} ")
            connect.commit()
    finally:
        connect.close()


def add_energy(user_id, num):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT energy, max_energy FROM users "
                           f"WHERE user_id={user_id}")
            energy_info = cursor.fetchone()
            user_energy = energy_info['energy']
            max_user_energy = energy_info['max_energy']
            if user_energy + num >= max_user_energy:
                cursor.execute(f"UPDATE users SET energy={max_user_energy} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
            else:
                cursor.execute(f"UPDATE users SET energy={user_energy + num} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
    finally:
        connect.close()
