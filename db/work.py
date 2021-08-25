from db.connection import get_connect
import random
import datetime


def create_personal_list_jobs(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users WHERE user_id={user_id} ")
            user_lvl = cursor.fetchone()['lvl']

            cursor.execute(f"SELECT * FROM jobs")
            jobs = cursor.fetchall()

            cursor.execute(f"SELECT * FROM user_jobs "
                           f"WHERE user_id={user_id}")
            user_jobs_now = cursor.fetchall()

            random.shuffle(jobs)
            user_jobs = jobs[:3]
            if not user_jobs_now:
                for job in user_jobs:
                    if job['need_strength'] != 0:
                        job['need_strength'] = job['need_strength'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_agility'] != 0:
                        job['need_agility'] = job['need_agility'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_intellect'] != 0:
                        job['need_intellect'] = job['need_intellect'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_luck'] != 0:
                        job['need_luck'] = job['need_luck'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    cursor.execute(
                        f"INSERT INTO user_jobs(user_id, job_id, need_strength, need_agility, need_intellect, need_luck) "
                        f"VALUES ({user_id}, {job['id']}, {job['need_strength']}, {job['need_agility']}, {job['need_intellect']}, {job['need_luck']}) ")
            else:
                cursor.execute(f"DELETE FROM user_jobs "
                               f"WHERE user_id={user_id} ")
                for job in user_jobs:
                    if job['need_strength'] != 0:
                        job['need_strength'] = job['need_strength'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_agility'] != 0:
                        job['need_agility'] = job['need_agility'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_intellect'] != 0:
                        job['need_intellect'] = job['need_intellect'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    if job['need_luck'] != 0:
                        job['need_luck'] = job['need_luck'] + user_lvl // job['lvl_div'] * job['lvl_mul']
                    cursor.execute(
                        f"INSERT INTO user_jobs(user_id, job_id, need_strength, need_agility, need_intellect, need_luck) "
                        f"VALUES ({user_id}, {job['id']}, {job['need_strength']}, {job['need_agility']}, {job['need_intellect']}, {job['need_luck']}) ")

            connect.commit()
    finally:
        connect.close()


def get_personal_jobs(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_jobs "
                           f"INNER JOIN jobs ON user_jobs.job_id=jobs.id WHERE user_id={user_id} ")
            jobs = cursor.fetchall()
            return jobs
    finally:
        connect.close()


def get_time_to_recreate_jobs(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"SELECT job_time FROM users "
                           f"WHERE user_id={user_id}")
            time_from_db = cursor.fetchone()['job_time']

            if time_from_db != None:
                delta = datetime.datetime.now() - time_from_db
                if delta.days >= 1:
                    cursor.execute(f"UPDATE users SET job_time='{now}' "
                                   f"WHERE user_id={user_id} ")
                    connect.commit()
                    return True
                else:
                    return False

            else:
                cursor.execute(f"UPDATE users SET job_time='{now}' "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return True

    finally:
        connect.close()


def get_job_by_name(user_id, job_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM user_jobs "
                           f"INNER JOIN jobs ON user_jobs.job_id=jobs.id WHERE name='{job_name}' AND user_id={user_id} ")

            job = cursor.fetchone()
            return job

    finally:
        connect.close()


def go_to_job(user_id, jod_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.datetime.now()
            end_work_time = now + datetime.timedelta(hours=2)
            end_work_time = end_work_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"UPDATE users SET end_job='{end_work_time}', on_job={1}, job_id={jod_id} "
                           f"WHERE user_id={user_id}")
            connect.commit()

    finally:
        connect.close()


def is_working(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT on_job FROM users "
                           f"wHERE user_id={user_id} ")
            on_job = cursor.fetchone()['on_job']
            if on_job == 1:
                return True
            else:
                return False

    finally:
        connect.close()


def end_job(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET end_job=NULL, on_job={0}, job_id=NULL "
                           f"WHERE user_id={user_id} ")
            connect.commit()

    finally:
        connect.close()


def choose_job_event(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            func_name = cursor.fetchone()['func_name']
            func_name = eval(func_name)
            return func_name(user_id)

    finally:
        connect.close()


def worker(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            user_money = hero_info['money']
            chance = random.randint(1, 100)

            if chance < 65 + hero_info['luck']:
                earn_money = (chance//10) * 3 + 50 + hero_info['strength'] * 5
                cursor.execute(f"UPDATE users SET money={user_money+earn_money}, exp={hero_info['exp']+2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '💰Отработали по царски. Вот ваше жалование.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 85 - hero_info['luck']:
                lost_thing = ['лопату', 'молоток', 'зубило', 'ведро', 'топор', 'совесть']
                lost_money = chance % 10 * 3 + 10
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                                   f"WHERE user_id={user_id} ")
                connect.commit()
                return f'Вы потеряли {random.choice(lost_thing)}' + '\n' + \
                           'Десятник очень вами не доволен и просит возместить убытки.' + '\n' + f'-{lost_money} Крон' + '\n' + '+4 опыта'

            else:
                earn_money = chance // 10 * 7 + 70
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 1}, energy={0} "
                               f"WHERE user_id={user_id} ")
                unluck_event = ['вы упали с лестницы', 'подскальзнулись на новом мраморном полу и разбили нос', 'подвернули ногу']
                connect.commit()
                return f'✅Усердно работая, {random.choice(unluck_event)}. Травма не большая, но придётся немного отдохнуть.' + '\n' + \
                        f'+{earn_money} крон' + '\n' + '+1 опыт'

    finally:
        connect.close()


def translator(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            chance = random.randint(1, 100)
            user_money = hero_info['money']

            if chance < 60 + hero_info['luck']:
                earn_money = hero_info['intellect'] * 5 + 40 + chance//10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '💰Хорошая работа. Вот ваши деньги.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 75 + hero_info['luck']:
                earn_money = hero_info['intellect'] * 3 + 30 + chance//10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '✅Вы так долго искали нужно слово в словаре, что едва не уснули. ' \
                       'Но работа сделана, не совсем так, как хотелось, конечно...' + '\n' + f'+{earn_money} Крон' + '\n' + '+3 опыта'

            else:
                lost_money = hero_info['intellect'] * 2 + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '❌Вы пролили кофе на манускрипт, теперь придётся платить компенсацию.' + '\n' + f'-{lost_money} Крон' + '\n' + '+4 опыта'

    finally:
        connect.close()


def courier(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            chance = random.randint(1, 100)
            user_money = hero_info['money']

            if chance < 65 + hero_info['luck']:
                earn_money = hero_info['agility'] * 5 + 30 + chance // 10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '💰Заказ доставлен вовремя. Клиент доволен, а значит самое время получить награду.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 70 + hero_info['luck']:
                bad_event = ['эльфиская статуэтка потеряла свои уши', 'фарфоровая ваза лишилась ручек', 'пицца осталась без колбасы', 'на портрете появилась лишняя родинка']
                earn_money = hero_info['agility'] + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'✅ По дороге вы умудрились несколько раз уронить посылку, и {random.choice(bad_event)}. ' \
                       f'Клиенту это не понравилось.' + '\n' + f'+{earn_money} Крон' + '\n' + '+3 опыта'

            else:
                lost_money = chance%10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'❌Вы опоздали на {random.randint(2, 4)} часа. ' \
                       f'Заказчик остался очень не довольным. Придётся платить штраф.' + '\n' + f'-{lost_money} Крон' + '\n' + '+4 опыта'

    finally:
        connect.close()


def blacksmith(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            chance = random.randint(1, 100)
            user_money = hero_info['money']

            if chance < 68 + hero_info['luck']:
                crafted_weapon = ['меч', 'алебарда', 'кираса', 'топор', 'лопата', 'нож']
                weapon_sex = {'меч': 1, 'алебарда': 0, 'кираса': 0, 'топор': 1, 'лопата': 0, 'нож': 1}
                random_weapon = random.choice(crafted_weapon)
                earn_money = hero_info['intellect'] * 3 + hero_info['strength'] * 4 + chance // 10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                if crafted_weapon[random_weapon] == 0:
                    return f'💰Отличная вышла {random_weapon}. Кузнец доволен твоей работой.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'
                else:
                    return f'💰Отличный вышел {random_weapon}. Кузнец доволен твоей работой.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 70 + hero_info['luck']:
                earn_money = hero_info['strength'] * 3 + hero_info['intellect'] + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'✅ Сегодня мастер кузнец работал над большим и сложным заказом. ' \
                       f'Вам оставалось только искать материалы и таскать дрова. Чтож, какая работа такое и жалование.. ' + \
                       f'Клиенту это не понравилось.' + '\n' + f'+{earn_money} Крон' + '\n' + '+3 опыта'

            else:
                lost_money = chance % 10 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'❌Вы опоздали на {random.randint(2, 4)} часа. ' \
                       f'— Что ты сделал с этой заготовкой?! Я так все заказы потеряю! ' \
                       f'[Дальше по эльфийски]. Вот так мастер кузнец отозвался о вашей работе. ' \
                       f'Может быть в другой раз выйдет лучше...' + '\n' + f'-{lost_money} Крон' + '\n' + '+4 опыта'

    finally:
        connect.close()


def tailor(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            chance = random.randint(1, 100)
            user_money = hero_info['money']

            if chance < 65 + hero_info['luck']:
                earn_money = hero_info['agility'] * 3 + hero_info['intellect'] * 4 + chance // 10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '💰 — Так, так... Шов на месте... Лишних дырок нет... Всё как надо! Деньги твои.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 70 + hero_info['luck']:
                earn_money = hero_info['agility'] + hero_info['intellect'] * 2 + 20 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'✅ Ты сломал несколько иголок, но с работой справился.. ' + '\n' + f'+{earn_money} Крон' + '\n' + '+3 опыта'

            else:
                random_1 = ['рукав', 'воротник', 'носок', 'чулок', 'пятку', 'капюшон', 'плащ']
                random_2 = ['рукаву', 'воротнику', 'носку', 'чулку', 'пятке', 'капюшону', 'плащу']
                lost_money = chance % 10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'❌— Пришить {random.choice(random_1)} к {random.choice(random_2)}!Да как так можно! ' \
                       f'[Дальше по эльфийски]. ' \
                       f'Вот что главный портной сказал о вашей работе.' + '\n' + f'-{lost_money} Крон'

    finally:
        connect.close()


def woodcutter(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN jobs ON jobs.id=users.job_id WHERE user_id={user_id} ")
            hero_info = cursor.fetchone()
            chance = random.randint(1, 100)
            user_money = hero_info['money']

            if chance < 65 + hero_info['luck']:
                earn_money = hero_info['agility'] * 4 + hero_info['strength'] * 3 + 40 + chance // 10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'💰 Сегодня даже выше нормы! Вот ваша заслуженная премия.' + '\n' + f'+{earn_money} Крон' + '\n' + '+2 опыта'

            elif chance < 70 + hero_info['luck']:
                fell_tree = ['сосна', 'ель', 'пихта', 'береза', 'лиственница', 'липа']
                earn_money = hero_info['strength'] * 2 + hero_info['agility'] * 2 + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3}, energy={0} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'✅ Это был бы обычный рабочий день... ' \
                       f'Если бы огромная {random.choice(fell_tree)} не упала вам на ногу. ' \
                       f'Придётся немного отдохнуть.' + '\n' + f'+{earn_money} Крон' + '\n' + '+3 опыта'

            else:
                lost_money = chance % 10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'❌Кажется вы зашли на чужую делянку. Придётся возместить убытки...' + '\n' + f'-{lost_money} Крон'

    finally:
        connect.close()
