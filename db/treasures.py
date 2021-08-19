from db.connection import get_connect
import random


def get_user_treasures(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT treasure_1, treasure_2, '
                           f'treasure_3, treasure_4, treasure_5, treasure_6, treasure_7 FROM users WHERE user_id={user_id}')
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

        
def unequip_item(hero_stats, item_stats):

    new_ATK = hero_stats['ATK'] - item_stats['ATK']
    new_HP = hero_stats['HP'] - item_stats['HP']
    new_MP = hero_stats['MP'] - item_stats['MP']
    new_strength = hero_stats['strength'] - item_stats['strength']
    new_agility = hero_stats['agility'] - item_stats['agility']
    new_intellect = hero_stats['intellect'] - item_stats['intellect']
    new_luck = hero_stats['luck'] - item_stats['luck']
    return {'new_ATK': new_ATK, 'new_HP': new_HP, 'new_MP': new_MP, 'new_strength': new_strength,
            'new_agility': new_agility, 'new_intellect': new_intellect, 'new_luck': new_luck}

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
                
            elif treasure_number == 7:

                result = random.randint(1,6)
                print(result)
                cursor.execute(f'SELECT * FROM pets '
                               f'INNER JOIN pets_stats ON pets.type=pets_stats.id '
                               f'WHERE owner_id={user_id} ')
                pet = cursor.fetchone()

                if result == 1:
                    earn_money = random.randint(1000, 5000)
                    earn_exp = random.randint(50, 100)
                    cursor.execute(f'UPDATE users SET money={user_money + earn_money}, '
                                   f'exp={user_exp + earn_exp}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()
                    return 'Вы открыли Ящик Пандоры и получили: ' + '\n' + f'+{earn_money} крон' + '\n' + f'+{earn_exp} опыта'

                elif result == 2:
                    print(user_info)
                    user_max_energy = user_info['max_energy']
                    print(user_max_energy)
                    cursor.execute(f'UPDATE users SET energy={0}, '
                                   f'max_energy={user_max_energy - 2}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()
                    return 'Открыв Ящик Пандоры, вы почувствовали некую слабость...'

                elif result == 3:

                    if pet:
                        earn_money = random.randint(1, 100)
                        cursor.execute(f'UPDATE users SET money={user_money+earn_money}, '
                                       f'{treasure}={user_treasure} '
                                       f'WHERE user_id={user_id}')
                        cursor.execute(f'SELECT * FROM pets '
                           f'INNER JOIN pets_stats ON pets.type=pets_stats.id '
                           f'WHERE owner_id={user_id} ')
                        pet_info = cursor.fetchone()
                        buff = pet_info['lvl'] // pet_info['lvl_buff'] + pet_info['add_how_many']

                        if pet_info['pet_func'] == 'default':
                            add_to = pet_info['add_to']

                            cursor.execute(f'SELECT {add_to} FROM users '
                                           f'WHERE user_id={user_id} ')
                            hero_stat = cursor.fetchone()[add_to]
                            new_hero_stat = hero_stat - buff

                            cursor.execute(f"UPDATE users SET {add_to}={new_hero_stat} "
                                           f"WHERE user_id={user_id}")
                        cursor.execute(f"DELETE FROM pets WHERE owner_id={user_id} ")
                        connect.commit()
                        return 'Когда вы открывали ящик, ваш питомец испугался яркого света и сбежал...' + '\n' + f'+ {earn_money} Крон'

                    else:
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

                        intellect = user_info['intellect']
                        strength = user_info['strength']
                        agility = user_info['agility']
                        cursor.execute(f"UPDATE users SET intellect={int(intellect*0.8)}, "
                                       f"strength={int(strength*0.8)}, "
                                       f"agility={int(agility*0.8)} "
                                       f"WHERE user_id={user_id}")
                        connect.commit()

                        return 'Из ящика выпрыгнул некий зверек, но при попытке его погладить, ' \
                               'он вас укусил и вы стали чувствовать себя некомфортно' + '\n' + f'+ {random_pet_name}'

                elif result == 4:
                    cursor.execute(f"SELECT id, name FROM items "
                                   f"WHERE tier={4}")
                    items = cursor.fetchall()
                    user_item = random.choice(items)
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {user_item['id']}) ")
                    cursor.execute(f'UPDATE users SET luck={-1}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()
                    return 'Вы открыли Ящик Пандоры и получили: ' + '\n' + f'+{user_item["name"]}.'\
                           + '\n' + 'Забрав находку, у вас появилось странное чувство...'

                elif result == 5:
                    weapon = user_info['weapon']
                    item_head = user_info['item_head']
                    item_body = user_info['item_body']
                    item_legs = user_info['item_legs']
                    item_artifact = user_info['item_artifact']

                    cursor.execute(f"SELECT * FROM relation_items_users "
                                   f"INNER JOIN items ON relation_items_users.item_id=items.id "
                                   f"WHERE relation_items_users.id={weapon}")
                    weapon = cursor.fetchone()
                    cursor.execute(f"SELECT * FROM relation_items_users "
                                   f"INNER JOIN items ON relation_items_users.item_id=items.id "
                                   f"WHERE relation_items_users.id={item_head}")
                    item_head = cursor.fetchone()
                    cursor.execute(f"SELECT * FROM relation_items_users "
                                   f"INNER JOIN items ON relation_items_users.item_id=items.id "
                                   f"WHERE relation_items_users.id={item_body}")
                    item_body = cursor.fetchone()
                    cursor.execute(f"SELECT * FROM relation_items_users "
                                   f"INNER JOIN items ON relation_items_users.item_id=items.id "
                                   f"WHERE relation_items_users.id={item_legs}")
                    item_legs = cursor.fetchone()
                    cursor.execute(f"SELECT * FROM relation_items_users "
                                   f"INNER JOIN items ON relation_items_users.item_id=items.id "
                                   f"WHERE relation_items_users.id={item_artifact}")
                    item_artifact = cursor.fetchone()

                    if weapon:
                        result = unequip_item(user_info, weapon)
                        cursor.execute(f"UPDATE users SET weapon=0 "
                                       f"WHERE user_id={user_id}")
                        cursor.execute(
                            f"UPDATE users SET ATK={result['new_ATK']}, "
                            f"HP={result['new_HP']}, "
                            f"MP={result['new_MP']}, "
                            f"strength={result['new_strength']}, "
                            f"agility={result['new_agility']}, "
                            f"intellect={result['new_intellect']}, "
                            f"luck={result['new_luck']} WHERE user_id={user_id}")

                    if item_head:
                        result = unequip_item(user_info, item_head)
                        cursor.execute(f"UPDATE users SET item_head=0 "
                                       f"WHERE user_id={user_id}")
                        cursor.execute(
                            f"UPDATE users SET ATK={result['new_ATK']}, "
                            f"HP={result['new_HP']}, "
                            f"MP={result['new_MP']}, "
                            f"strength={result['new_strength']}, "
                            f"agility={result['new_agility']}, "
                            f"intellect={result['new_intellect']}, "
                            f"luck={result['new_luck']} WHERE user_id={user_id}")

                    if item_body:
                        result = unequip_item(user_info, item_body)
                        cursor.execute(f"UPDATE users SET item_body=0 "
                                       f"WHERE user_id={user_id}")
                        cursor.execute(
                            f"UPDATE users SET ATK={result['new_ATK']}, "
                            f"HP={result['new_HP']}, "
                            f"MP={result['new_MP']}, "
                            f"strength={result['new_strength']}, "
                            f"agility={result['new_agility']}, "
                            f"intellect={result['new_intellect']}, "
                            f"luck={result['new_luck']} WHERE user_id={user_id}")

                    if item_legs:
                        result = unequip_item(user_info, item_legs)
                        cursor.execute(f"UPDATE users SET item_legs=0 "
                                       f"WHERE user_id={user_id}")
                        cursor.execute(
                            f"UPDATE users SET ATK={result['new_ATK']}, "
                            f"HP={result['new_HP']}, "
                            f"MP={result['new_MP']}, "
                            f"strength={result['new_strength']}, "
                            f"agility={result['new_agility']}, "
                            f"intellect={result['new_intellect']}, "
                            f"luck={result['new_luck']} WHERE user_id={user_id}")

                    if item_artifact:
                        result = unequip_item(user_info, item_artifact)
                        cursor.execute(f"UPDATE users SET item_artifact=0 "
                                       f"WHERE user_id={user_id}")
                        cursor.execute(
                            f"UPDATE users SET ATK={result['new_ATK']}, "
                            f"HP={result['new_HP']}, "
                            f"MP={result['new_MP']}, "
                            f"strength={result['new_strength']}, "
                            f"agility={result['new_agility']}, "
                            f"intellect={result['new_intellect']}, "
                            f"luck={result['new_luck']} WHERE user_id={user_id}")

                    cursor.execute(f"DELETE FROM relation_items_users WHERE user_id={user_id} ")

                    cursor.execute(f"SELECT id, name FROM items "
                                   f"WHERE tier={4}")
                    items = cursor.fetchall()
                    user_item_1 = random.choice(items)
                    user_item_2 = random.choice(items)

                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {user_item_1['id']}) ")
                    cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                                   f"VALUES ({user_id}, {user_item_2['id']}) ")
                    cursor.execute(f'UPDATE users SET {treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()

                    return 'Вы открыли Ящик Пандоры и получили: ' + '\n' + f'+{user_item_2["name"]}' + '\n' + f'+{user_item_1["name"]}' + "\n" + \
                           'Ваш рюкзак показался вам легче...'

                elif result == 6:
                    user_luck = user_info['luck']
                    cursor.execute(f'UPDATE users SET luck={user_luck + 10}, money={0}, is_dead={1}, '
                                   f'{treasure}={user_treasure} '
                                   f'WHERE user_id={user_id}')
                    connect.commit()
                    return 'Вы открыли Ящик Пандоры и из него нахлынул якрий свет. Вы потеряли сознание. ' \
                           'Очнувшись, вы поняли, что пока вы спали, вас избили и обокрыли...' + '\n' + '+10 удачи'
            
    finally:
        connect.close()
