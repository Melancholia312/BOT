import datetime
import random
from time import strftime
from time import gmtime
from db.connection import get_connect
food = {'конфета': 2, 'морковка': 4, 'хлеб': 7}


def get_user_pet(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT * FROM pets '
                           f'INNER JOIN pets_stats ON pets.type=pets_stats.id '
                           f'WHERE owner_id={user_id} ')
            pet = cursor.fetchone()
            return pet
    finally:
        connect.close()


def give_pet(user_id, pet_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"INSERT INTO pets(owner_id, type, name) "
                           f"VALUES ({user_id}, {pet_id}, 'Без клички') ")

            cursor.execute(f'SELECT * FROM pets_stats '
                           f'WHERE id={pet_id} ')
            pets_stats = cursor.fetchone()
            if pets_stats['pet_func'] == 'default':
                add_to = pets_stats['add_to']
                add_how_many = pets_stats['add_how_many']

                cursor.execute(f'SELECT {add_to} FROM users '
                               f'WHERE user_id={user_id} ')
                hero_stat = cursor.fetchone()[add_to]
                new_hero_stat = hero_stat + add_how_many

                cursor.execute(f"UPDATE users SET {add_to}={new_hero_stat} "
                               f"WHERE user_id={user_id}")

            connect.commit()
    finally:
        connect.close()


def dig(user_id, dog_lvl):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            chance = random.randint(1, 100)
            if chance < dog_lvl//20:
                cursor.execute(f'SELECT id, name FROM items WHERE tier={4}')
                items = cursor.fetchall()
                new_item = random.choice(items)
                new_item_id = new_item['id']
                new_item_name = new_item['name']
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {new_item_id}) ")
                return f'Ваша собака выкопала {new_item_name}. Такого просто не может быть...'

            elif chance < dog_lvl//14:
                cursor.execute(f'SELECT id, name FROM items WHERE tier={3}')
                items = cursor.fetchall()
                new_item = random.choice(items)
                new_item_id = new_item['id']
                new_item_name = new_item['name']
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {new_item_id}) ")
                return f'Ваша собака выкопала {new_item_name}. Невероятно!'

            elif chance < dog_lvl//10:
                cursor.execute(f'SELECT id, name FROM items WHERE tier={2}')
                items = cursor.fetchall()
                new_item = random.choice(items)
                new_item_id = new_item['id']
                new_item_name = new_item['name']
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {new_item_id}) ")
                return f'Ваша собака выкопала {new_item_name}'

            elif chance < dog_lvl//4:
                cursor.execute(f'SELECT id, name FROM items WHERE tier={1}')
                items = cursor.fetchall()
                new_item = random.choice(items)
                new_item_id = new_item['id']
                new_item_name = new_item['name']
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {new_item_id}) ")
                return f'Ваша собака выкопала {new_item_name}'

            elif chance < dog_lvl*3 + 25:
                earn_money = random.randint(dog_lvl + 60, dog_lvl*2 + 60)
                cursor.execute(f"SELECT money FROM users "
                               f"WHERE user_id={user_id}")
                user_money_info = cursor.fetchone()
                user_money = user_money_info['money']
                user_money = user_money + earn_money
                cursor.execute(f"UPDATE users SET money={user_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return f'Ваша собака выкопала {earn_money} крон'

            else:
                return f'В этот раз ваша собака не выкопала ничего ценного...'

    finally:
        connect.close()


def feed_pet(user_id, food_exp):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT * FROM pets '
                           f'INNER JOIN pets_stats ON pets.type=pets_stats.id '
                           f'WHERE owner_id={user_id} ')
            pet_info = cursor.fetchone()
            new_pet_exp = pet_info['exp'] + food_exp
            max_pet_exp = pet_info['max_exp']
            pet_lvl = pet_info['lvl']
            answer = 'Вы покормили вашего питомца' + '\n'

            now = datetime.datetime.now()
            pet_feed_time = now + datetime.timedelta(hours=12)
            pet_feed_time = pet_feed_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE pets SET eat_time='{pet_feed_time}' "
                           f"WHERE owner_id={user_id} ")

            if new_pet_exp >= max_pet_exp:
                new_pet_lvl = pet_lvl + 1
                new_pet_max_exp = 7 + new_pet_lvl // 3 * 5
                cursor.execute(f"UPDATE pets SET exp={new_pet_exp - max_pet_exp}, lvl={new_pet_lvl}, max_exp={new_pet_max_exp} "
                               f"WHERE owner_id={user_id}")
                answer += f'Ваш питомец достиг {new_pet_lvl} уровень!' + '\n'
                if pet_info['pet_func'] == 'default':
                    pet_lvl_buff = pet_info['lvl_buff']
                    if new_pet_lvl % pet_lvl_buff == 0:
                        add_to = pet_info['add_to']
                        cursor.execute(f'SELECT {add_to} FROM users '
                                       f'WHERE user_id={user_id} ')
                        hero_stat = cursor.fetchone()[add_to]
                        lvl_add_buff = pet_info['lvl_add_buff']
                        new_hero_stat = hero_stat + lvl_add_buff
                        cursor.execute(f"UPDATE users SET {add_to}={new_hero_stat} "
                                       f"WHERE user_id={user_id}")
                        answer += 'Ваш питомец улучшил ваши характеристики!'
                else:
                    pet_func = pet_info['pet_func']
                    pet_func = eval(pet_func)
                    connect.commit()
                    return answer + pet_func(user_id, new_pet_lvl)

            else:
                cursor.execute(f"UPDATE pets SET exp={new_pet_exp} "
                               f"WHERE owner_id={user_id}")
            connect.commit()
            return answer

    finally:
        connect.close()


def get_time_to_feed(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT eat_time FROM pets "
                           f"WHERE owner_id={user_id}")

            try:
                time_from_db = cursor.fetchone()['eat_time']
            except:
                time_from_db = None

            if time_from_db != None:
                delta = time_from_db - datetime.datetime.now()
                seconds = delta.seconds
                days = delta.days
                if seconds > 43200 or days < 0:
                    return [True]
                else:
                    remaining_time = strftime("%H:%M", gmtime(seconds))
                    return False, f'Еще рано. До следующей кормежки осталось {remaining_time}'


            else:
                return [True]

    finally:
        connect.close()


def change_pet_name(user_id, pet_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE pets SET name='{pet_name}' "
                           f"WHERE owner_id={user_id}")
            connect.commit()
    finally:
        connect.close()
        
        
def let_go_pet(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"DELETE FROM pets WHERE owner_id={user_id} ")
            connect.commit()
    finally:
        connect.close() 

