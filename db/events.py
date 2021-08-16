import random

from db.connection import get_connect
import datetime


def in_expedition(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT in_expedition FROM users "
                           f"WHERE user_id={user_id} ")
            result = cursor.fetchone()['in_expedition']

            if result == 1:
                return True
            else:
                return False

    finally:
        connect.close()


def end_expedition(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET expedition_time=NULL, in_expedition=0 "
                           f"WHERE user_id={user_id} ")
            connect.commit()

    finally:
        connect.close()


def go_to_expedition(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.datetime.now()
            end_expedition_time = now + datetime.timedelta(hours=1)
            end_expedition_time = end_expedition_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE users SET expedition_time='{end_expedition_time}', in_expedition=1 "
                           f"WHERE user_id={user_id}")
            connect.commit()

    finally:
        connect.close()


def choose_event(user_id):
    events = [old_carriage, black_cat, tavern, find_joke, event_sleep, find_murder, find_homeless, street_walk, merchant, chimera_nest, swamp]
    rand_func = random.choice(events)
    return rand_func(user_id)


def black_cat(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT luck FROM users "
                           f"WHERE user_id={user_id} ")
            luck = cursor.fetchone()['luck']
            luck -= 1
            cursor.execute(f"UPDATE users SET luck={luck} "
                           f"WHERE user_id={user_id} ")
            connect.commit()
            return 'Чёрный кот перебежал вам дорогу' + '\n' + \
                   '-1 удача' + '\n\n' + '~~~'

    finally:
        connect.close()


def old_carriage(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            num_events = [1, 2]
            num_event = random.choice(num_events)
            cursor.execute(f"SELECT money, name, agility, exp FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            money = hero_info['money']
            hero_name = hero_info['name']
            hero_agility = hero_info['agility']
            hero_exp = hero_info['exp']
            earn_money = random.randint(50, 200)
            money += earn_money
            answer = 'Вы наткнулись на разграбленную повозку. Интересно, чьих это рук дело ?' + '\n' + \
                     f'+{earn_money} Крон' + '\n\n' + '~~~\n'
            cursor.execute(f"UPDATE users SET money={money} "
                           f"WHERE user_id={user_id} ")
            if num_event == 1:
                wolf_events = [1,2]
                wolf_event = random.choice(wolf_events)
                answer += 'Вы услышали волчий вой. Похоже здесь очень скоро будет крупная стая диких зверей.' + '\n\n' + '~~~\n'
                if wolf_event == 1:
                    hero_exp += 2
                    answer += f'- {hero_name} успел сбежать. Всё закончилось хорошо.' + '\n' +\
                              '+ 2 опыт' + '\n\n' + '~~~\n'
                    cursor.execute(f"UPDATE users SET exp={hero_exp} "
                                   f"WHERE user_id={user_id} ")
                    return answer
                else:
                    wolf_nums_fight = [1,2,3]
                    wolf_num_fight = random.choice(wolf_nums_fight)
                    answer += 'Отступать некуда, придётся принять бой.' + '\n'
                    if wolf_num_fight == 1:
                        answer += 'Вам удалось без потерь перебить всю стаю.' + '\n' + \
                                  '+4 опыта' + '\n\n' + '~~~\n'
                        hero_exp += 4
                        cursor.execute(f"UPDATE users SET exp={hero_exp} "
                                       f"WHERE user_id={user_id} ")
                        connect.commit()
                        return answer

                    elif wolf_num_fight == 2:
                        answer += 'Один серый волк подкрался к вам сзади и укусил за голень! Ваша нога ещё долго будет восстанавливаться.' + '\n' + \
                                  '-1 Ловкость' + '\n' + '+2 опыт' + '\n\n' + '~~~\n'
                        hero_agility -= 1
                        hero_exp += 2
                        cursor.execute(f"UPDATE users SET agility={hero_agility}, exp={hero_exp} "
                                       f"WHERE user_id={user_id} ")
                        connect.commit()
                        return answer
                    else:
                        money = round(money * 0.85)
                        hero_exp += 3
                        cursor.execute(f"UPDATE users SET money={money}, exp={hero_exp} "
                                       f"WHERE user_id={user_id} ")
                        answer += 'К вам на помощь подоспел отряд вольных стрелков. Все звери убиты, но теперь придётся отблагодарить ваших спасителей звонков монетой.' + '\n' + \
                                  '-15% Крон' + ' ' + '+ 3 опыта' + '\n\n' + '~~~\n'
                        connect.commit()
                        return answer

            elif num_event == 2:
                quantity_bandits = random.randint(3,5)
                answer += f'Пройдя по следам, вы встретили {quantity_bandits} бандитов.' + '\n\n' + '~~~\n'
                bandits_events = [1,2]
                bandits_event = random.choice(bandits_events)
                
                if bandits_event == 1:
                    bandits_money = random.randint(50, 125)
                    money += bandits_money
                    answer += 'Вы не смогли найти общий язык с головорезами и пришлось их перебить.' + '\n' + \
                              f'+ {bandits_money} монет.' + '\n\n' + '~~~\n'
                    cursor.execute(f"UPDATE users SET money={money} "
                                   f"WHERE user_id={user_id} ")
                    connect.commit()
                    return answer
                else:
                    random_exp = random.randint(2,4)
                    answer += 'Отличные оказались ребята. Поели, попили и обсудили актуальные проблемы нашего нелегкого ремесла.' + '\n'+ \
                              f'+{random_exp} опыта.' + '\n\n' + '~~~\n'
                    cursor.execute(f"UPDATE users SET exp={random_exp} "
                                   f"WHERE user_id={user_id} ")
                    connect.commit()
                    return answer
    finally:
        connect.close()


def tavern(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT intellect, exp FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            intellect = hero_info['intellect'] + 1
            hero_exp = hero_info['exp'] + 2
            cursor.execute(f"UPDATE users SET intellect={intellect}, exp={hero_exp} "
                           f"WHERE user_id={user_id}")
            connect.commit()
            return 'В трактире, за кружкой вашего любимого дешёвого пива, вы подслушали разговор двух чародеев ' + '\n' \
                   '+ 1 Интеллект' + '\n' + '+ 2 опыт' + '\n\n' + '~~~\n'
    finally:
        connect.close()


def find_joke(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT exp, money FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            money = hero_info['money']
            exp = hero_info['exp']
            jokes = ['Идёт медведь по лесу, видит - повозка горит. Сел в неё и сгорел.']
            answer = 'Вы нашли вырваную страницу из Большого сборника анекдотов!' + '\n' + \
                     '+2 опыт' + '\n\n' + '~~~\n'
            exp += 2
            answer += random.choice(jokes) + '\n'
            answer += 'Ваш смех разбудил медведя-переростка. Похоже предстоит трудный бой.' + '\n\n' + '~~~\n'
            random_events = [1,2]
            random_event = random.choice(random_events)
            if random_event == 1:
                answer += 'Убегая, вы обронили несколько монет.' + '\n' + \
                          '-5% Крон.' + '\n\n' + '~~~\n'
                money = money * 0.95
                cursor.execute(f"UPDATE users SET money={money}, exp={exp} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
            else:
                answer += 'Вы победили! Теперь можно и выпить' + '\n' + \
                          '+5 опыта' + '\n\n' + '~~~\n'
                exp += 5
                cursor.execute(f"UPDATE users SET exp={exp} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer

    finally:
        connect.close()


def find_murder(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT strength, exp FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            strength = hero_info['strength']
            hero_exp = hero_info['exp']
            random_events = [1,2]
            random_event = random.choice(random_events)
            answer = 'Вы встретили орка-наёмника и решили померится с ним силами в традиционной орчей игре manmano.' + '\n'
            if random_event == 1:
                answer += 'Ваш новый знакомый оказался сильней. Но ничего, в следующий раз повезёт' + '\n' + \
                          '+4 Опыта' + '\n\n' + '~~~\n'
                cursor.execute(f"UPDATE users SET strength={strength}, exp={hero_exp+4} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
            else:
                answer += 'Вы победили!' + '\n' + \
                          '+1 Сила' + ' ' + '+2 опыт' + '\n\n' + '~~~\n' 
                cursor.execute(f"UPDATE users SET strength={strength + 1}, exp={hero_exp + 2} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
    finally:
        connect.close()


def find_homeless(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT money, exp, name, luck FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            hero_money = hero_info['money']
            hero_luck = hero_info['luck']
            hero_name = hero_info['name']
            random_events = [1, 2]
            random_event = random.choice(random_events)
            answer = 'На улице города, вы встретили нищего. Он просил милостню..' + '\n\n' + '~~~\n'
            if random_event == 1:
                answer += f'Конечно, {hero_name} добрая душа. Вы не смогли пройти мимо и бросили пару монет в чашку нищего.' + '\n' + \
                          '-5% монет' + ' ' + '+1 удача' + '\n\n' + '~~~\n' 
                hero_money = int(hero_money * 0.95)
                cursor.execute(f"UPDATE users SET luck={hero_luck + 1}, money={hero_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
            else:
                answer += 'Вы прошли мимо нищего, даже не заметив его.' + '\n\n' + '~~~\n'
                return answer
    finally:
        connect.close()


def street_walk(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT money, exp, name, luck FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            hero_money = hero_info['money']
            hero_exp = hero_info['exp']
            hero_luck = hero_info['luck']
            hero_name = hero_info['name']
            random_events = [1, 2]
            random_event = random.choice(random_events)
            answer = 'Гуляя по городу, вы заметили как у одного очень важного господина выпал кошелёк.' + '\n' + \
                     '+1 опыт' + '\n\n' + '~~~\n'
            hero_exp += 1
            if random_event == 1:
                steal_money = random.randint(100, 300)
                answer += f'Стараясь не привлекать внимание, вы подобрали его и поспешили зайти за угол, чтобы оценить вашу находку.' + '\n' + \
                          f'+ {steal_money} Крон' + '\n\n' + '~~~\n'
                hero_money += steal_money
                cursor.execute(f"UPDATE users SET exp={hero_exp}, money={hero_money} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
            else:
                answer += f'{hero_name} честный человек. И потому, не задумываясь, вы догнали того господина и вернули пропажу.' + '\n' + \
                          '+4 опыта +1 удача' + '\n\n' + '~~~\n'
                hero_exp += 4
                hero_luck += 1
                cursor.execute(f"UPDATE users SET luck={hero_luck}, exp={hero_exp} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return answer
    finally:
        connect.close()


def event_sleep(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT exp FROM users "
                           f"WHERE user_id={user_id} ")
            exp = cursor.fetchone()['exp']
            exp += 3
            cursor.execute(f"UPDATE users SET exp={exp} "
                           f"WHERE user_id={user_id} ")
            answer = 'Вы заснули на опушке леса.' + '\n' + \
                     '+3 опыта' + '\n' + '~~~~~~~~' + '\n'

            cursor.execute(f'SELECT id FROM pets '
                           f'WHERE owner_id={user_id} ')
            pet = cursor.fetchone()
            chance = random.randint(1, 100)
            if not pet and chance < 35:
                random_event = [1,2]
                random_event = random.choice(random_event)
                if random_event == 1:
                    answer += 'Вы проснулись от странного шороха, похоже кто-то решил полакомится вашими запасами.' + '\n'
                    answer += 'Вы аккуратно заглянули в сумку...' + '\n'
                    answer += 'Там сидел белый кролик!' + '\n' + '\n'
                    answer += 'Теперь у вас появился новый питомец.'
                    pet_id = 5
                else:
                    pet_id = 7
                    answer += 'Вы проснулись от ощущения тяжести. Похоже дикий кот уснул у вас на груди. Теперь он домашний.'

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
            return answer
    finally:
        connect.close()


def merchant(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT exp, money FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            exp = hero_info['exp']
            money = hero_info['money']
            exp += 2
            answer = 'На рынке вы увидели как местный купец или какой-то ' \
                     'подозрительный тип или сапожник или путешественник в ' \
                     'потрепаном костюме продаёт хорошую ездовую лошадь за 120 крон.' + '\n' + \
                     '+2 опыта' + '\n' + '~~~~~~~~' + '\n'

            cursor.execute(f'SELECT id FROM pets '
                           f'WHERE owner_id={user_id} ')
            pet = cursor.fetchone()
            chance = random.randint(1, 100)

            if not pet and money >= 120 and chance < 35:
                answer += 'Недолго думаю, вы отдали деньги тому продавцу.' + '\n'
                answer += 'Теперь у вас появилась лошадь!' + '\n'
                answer += '-120 крон'
                pet_id = 4
                money -= 120
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
            else:
                answer += 'Вы прошли мимо и сэкономили немного монет.' + '\n'
                answer += '+2 опыта'
                exp += 2

            cursor.execute(f"UPDATE users SET exp={exp}, money={money} "
                           f"WHERE user_id={user_id} ")

            connect.commit()
            return answer
    finally:
        connect.close()


def chimera_nest(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT exp, money FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            exp = hero_info['exp']
            money = hero_info['money']
            exp += 2
            earn_money = random.randint(10, 30)
            money += earn_money
            answer = 'Вы наткнулись на разоренное гнездо химеры.' + '\n' + \
                     '+2 опыта' + '\n' + '~~~~~~~~' + '\n'

            answer += 'В нем лежало несколько монет, кости и сундук странного вида.' + '\n'
            answer += f'+{earn_money} крон' + '\n'
            answer += '+Зачарованный сундук' + '\n' + '~~~~~~~~' + '\n'
            treasure = f'treasure_{2}'
            cursor.execute(f'SELECT {treasure} FROM users WHERE user_id={user_id}')
            treasure_quantity = cursor.fetchone()[treasure] + 1
            cursor.execute(f'UPDATE users SET {treasure}={treasure_quantity} '
                           f'WHERE user_id={user_id}')

            cursor.execute(f'SELECT id FROM pets '
                           f'WHERE owner_id={user_id} ')
            pet = cursor.fetchone()
            chance = random.randint(1, 100)

            if not pet and chance < 35:
                answer += 'Растроенные тем, что кто-то вас опередил, вы швырнули самый большой мосол куда-то в даль.' + '\n' + '~~~~~~~~' + '\n'
                answer += 'Через некоторое время прибежала собака с этим мослом в зубах. Похоже теперь у вас появился новый друг!'
                pet_id = 3
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

            cursor.execute(f"UPDATE users SET exp={exp}, money={money} "
                           f"WHERE user_id={user_id} ")

            connect.commit()
            return answer
    finally:
        connect.close()


def swamp(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT exp, intellect FROM users "
                           f"WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            exp = hero_info['exp']
            intellect = hero_info['intellect']
            exp += 3
            answer = 'Заблудившись в лесу, вы наткнулись на болото.' + '\n' + 'Может быть там найдётся что-нибудь интересное ?' + '\n' + \
                     '+3 опыта' + '\n' + '~~~~~~~~' + '\n'

            cursor.execute(f'SELECT id FROM pets '
                           f'WHERE owner_id={user_id} ')
            pet = cursor.fetchone()
            chance = random.randint(1, 100)

            if not pet and chance < 35:
                answer += 'Вы ничего не нашли. Как утешительный приз, вы решили забрать жабу.' + '\n' + 'Теперь у вас есть домашняя жаба!'
                pet_id = 2
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

            elif chance < 60:
                answer += 'Не глубоко в воде лежала бутылка с запиской.' + '\n'
                answer += '+ Бутылка с письмом'
                treasure = f'treasure_{5}'
                cursor.execute(f'SELECT {treasure} FROM users WHERE user_id={user_id}')
                treasure_quantity = cursor.fetchone()[treasure] + 1
                cursor.execute(f'UPDATE users SET {treasure}={treasure_quantity} '
                               f'WHERE user_id={user_id}')
            else:
                answer += 'Вы ничего не нашли в этом противном болоте. Только зря испачкались...' + '\n' + '-1 интеллект'
                intellect -= 1

            cursor.execute(f"UPDATE users SET exp={exp}, intellect={intellect} "
                           f"WHERE user_id={user_id} ")

            connect.commit()
            return answer
    finally:
        connect.close()
