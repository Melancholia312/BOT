from db.connection import get_connect
import random


def get_user_treasures(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT treasure_1, treasure_2, '
                           f'treasure_3, treasure_4, treasure_5, treasure_6 FROM users WHERE user_id={user_id}')
            treasures = cursor.fetchone()
            return treasures

    finally:
        connect.close()


def give_treasure(user_id, treasure_number, treasure_quantity=1):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            treasure = f'treasure_{treasure_number}'
            cursor.execute(f'SELECT {treasure} FROM users WHERE user_id={user_id}')
            treasure_quantity = cursor.fetchone()[treasure] + treasure_quantity
            cursor.execute(f'UPDATE users SET {treasure}={treasure_quantity} '
                           f'WHERE user_id={user_id}')
            connect.commit()

    finally:
        connect.close()


def check_treasure_quantity(user_id, treasure_number):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            treasure = f'treasure_{treasure_number}'
            cursor.execute(f'SELECT {treasure} FROM users WHERE user_id={user_id}')
            treasure_quantity = cursor.fetchone()[treasure]
            if treasure_quantity > 0:
                return True
            else:
                return False

    finally:
        connect.close()


def open_treasure(user_id, treasure_number):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            treasure = f'treasure_{treasure_number}'
            cursor.execute(f'SELECT exp, money, {treasure} FROM users WHERE user_id={user_id}')
            user_info = cursor.fetchone()
            user_exp = user_info['exp']
            user_money = user_info['money']
            user_treasure = user_info[treasure] - 1
            if treasure_number == 1:
                earn_exp = random.randint(3, 6)
                earn_money = random.randint(75, 125)

                cursor.execute(f'SELECT id, name FROM items WHERE tier={1}')
                items = cursor.fetchall()
                new_item = random.choice(items)
                new_item_id = new_item['id']
                new_item_name = new_item['name']
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {new_item_id}) ")

                cursor.execute(f'UPDATE users SET money={user_money+earn_money}, '
                               f'exp={user_exp+earn_exp}, '
                               f'{treasure}={user_treasure} '
                               f'WHERE user_id={user_id}')
                connect.commit()

                return 'Вы открыли Дорожный сундук и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта' + '\n' + f'+ {new_item_name}'

            elif treasure_number == 2:

                earn_exp = random.randint(1, 10)
                earn_money = random.randint(10, 250)
                chance = random.randint(1, 100)

                if chance < 20:
                    cursor.execute(f'SELECT id, name FROM items WHERE tier={2}')
                    items = cursor.fetchall()
                    new_item = random.choice(items)
                    new_item_id = new_item['id']
                    new_item_name = new_item['name']
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {new_item_id}) ")

                    cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                                   f'exp={user_exp + earn_exp}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Зачарованный сундук и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта' + '\n' + f'+ {new_item_name}'

                elif chance < 60:

                    cursor.execute(f'SELECT id, name FROM items WHERE tier={1}')
                    items = cursor.fetchall()
                    new_item = random.choice(items)
                    new_item_id = new_item['id']
                    new_item_name = new_item['name']
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {new_item_id}) ")

                    cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                                   f'exp={user_exp + earn_exp}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Зачарованный сундук и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта' + '\n' + f'+ {new_item_name}'

                else:
                    cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                                   f'exp={user_exp + earn_exp}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()
                    return 'Вы открыли Зачарованный сундук и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта'

            elif treasure_number == 3:

                chance = random.randint(1, 100)

                if chance < 50:
                    cursor.execute(f'SELECT id, name FROM items WHERE tier={2}')
                    items = cursor.fetchall()
                    new_item = random.choice(items)
                    new_item_id = new_item['id']
                    new_item_name = new_item['name']
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {new_item_id}) ")

                    cursor.execute(f'UPDATE users SET {treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Аукционный сундук и получили: ' + '\n' + f'+ {new_item_name}'

                else:

                    cursor.execute(f'SELECT id, name FROM items WHERE tier={3}')
                    items = cursor.fetchall()
                    new_item = random.choice(items)
                    new_item_id = new_item['id']
                    new_item_name = new_item['name']
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {new_item_id}) ")

                    cursor.execute(f'UPDATE users SET {treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Аукционный сундук и получили: ' + '\n' + f'+ {new_item_name}'

            elif treasure_number == 4:

                earn_exp = random.randint(18, 23)
                earn_money = random.randint(600, 750)

                cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                               f'exp={user_exp + earn_exp}, '
                               f'{treasure}={user_treasure} '
                               f'WHERE user_id={user_id}')
                connect.commit()

                return 'Вы открыли Потерянную шкатулку и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта'

            elif treasure_number == 5:

                earn_exp = random.randint(12, 17)
                earn_money = random.randint(250, 300)

                cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                               f'exp={user_exp + earn_exp}, '
                               f'{treasure}={user_treasure} '
                               f'WHERE user_id={user_id}')
                connect.commit()

                return 'Вы открыли Бутылку с письмом  и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта'
            
            elif treasure_number == 6:

                cursor.execute(f'SELECT pet_name FROM pets '
                               f'INNER JOIN pets_stats ON pets.type=pets_stats.id '
                               f'WHERE owner_id={user_id} ')
                user_pet = cursor.fetchone()
                if not user_pet:
                    cursor.execute(f'SELECT * FROM pets_stats')
                    pets = cursor.fetchall()
                    random_pet = random.choice(pets)
                    random_pet_id = random_pet['id']
                    random_pet_name = random_pet['pet_name']
                    cursor.execute(f"INSERT INTO pets(owner_id, type, name) "
                                   f"VALUES ({user_id}, {random_pet_id}, 'Без клички') ")

                    cursor.execute(f'SELECT * FROM pets_stats '
                                   f'WHERE id={random_pet_id} ')
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

                        cursor.execute(f'UPDATE users SET {treasure}={user_treasure} '
                                       f'WHERE user_id={user_id}')

                    connect.commit()
                    return 'Вы открыли Мяукающий мешок и получили: ' + '\n' + f'+{random_pet_name}'

                else:
                    earn_exp = random.randint(12, 17)
                    earn_money = random.randint(300, 500)
                    cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                                   f'exp={user_exp + earn_exp}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Мяукающий мешок и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта'
            
    finally:
        connect.close()
