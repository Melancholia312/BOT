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
                return '???????????????????????? ???? ????????????. ?????? ???????? ??????????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 85 - hero_info['luck']:
                lost_thing = ['????????????', '??????????????', '????????????', '??????????', '??????????', '??????????????']
                lost_money = chance % 10 * 3 + 10
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                                   f"WHERE user_id={user_id} ")
                connect.commit()
                return f'???? ???????????????? {random.choice(lost_thing)}' + '\n' + \
                           '???????????????? ?????????? ???????? ???? ?????????????? ?? ???????????? ???????????????????? ????????????.' + '\n' + f'-{lost_money} ????????' + '\n' + '+4 ??????????'

            else:
                earn_money = chance // 10 * 7 + 70
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 1}, energy={0} "
                               f"WHERE user_id={user_id} ")
                unluck_event = ['???? ?????????? ?? ????????????????', '?????????????????????????????? ???? ?????????? ?????????????????? ???????? ?? ?????????????? ??????', '???????????????????? ????????']
                connect.commit()
                return f'????????????????? ??????????????, {random.choice(unluck_event)}. ???????????? ???? ??????????????, ???? ???????????????? ?????????????? ??????????????????.' + '\n' + \
                        f'+{earn_money} ????????' + '\n' + '+1 ????????'

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
                return '?????????????????? ????????????. ?????? ???????? ????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 75 + hero_info['luck']:
                earn_money = hero_info['intellect'] * 3 + 30 + chance//10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '??????? ?????? ?????????? ???????????? ?????????? ?????????? ?? ??????????????, ?????? ???????? ???? ????????????. ' \
                       '???? ???????????? ??????????????, ???? ???????????? ??????, ?????? ????????????????, ??????????????...' + '\n' + f'+{earn_money} ????????' + '\n' + '+3 ??????????'

            else:
                lost_money = hero_info['intellect'] * 2 + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return '??????? ?????????????? ???????? ???? ????????????????????, ???????????? ???????????????? ?????????????? ??????????????????????.' + '\n' + f'-{lost_money} ????????' + '\n' + '+4 ??????????'

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
                return '?????????????? ?????????????????? ??????????????. ???????????? ??????????????, ?? ???????????? ?????????? ?????????? ???????????????? ??????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 70 + hero_info['luck']:
                bad_event = ['?????????????????? ?????????????????? ???????????????? ???????? ??????', '???????????????????? ???????? ???????????????? ??????????', '?????????? ???????????????? ?????? ??????????????', '???? ???????????????? ?????????????????? ???????????? ??????????????']
                earn_money = hero_info['agility'] + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??? ???? ???????????? ???? ???????????????????? ?????????????????? ?????? ?????????????? ??????????????, ?? {random.choice(bad_event)}. ' \
                       f'?????????????? ?????? ???? ??????????????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+3 ??????????'

            else:
                lost_money = chance%10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??????? ???????????????? ???? {random.randint(2, 4)} ????????. ' \
                       f'???????????????? ?????????????? ?????????? ???? ??????????????????. ???????????????? ?????????????? ??????????.' + '\n' + f'-{lost_money} ????????' + '\n' + '+4 ??????????'

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
                crafted_weapon = ['??????', '????????????????', '????????????', '??????????', '????????????', '??????']
                weapon_sex = {'??????': 1, '????????????????': 0, '????????????': 0, '??????????': 1, '????????????': 0, '??????': 1}
                random_weapon = random.choice(crafted_weapon)
                earn_money = hero_info['intellect'] * 3 + hero_info['strength'] * 4 + chance // 10 * 2
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 2} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                if crafted_weapon[random_weapon] == 0:
                    return f'???????????????????? ?????????? {random_weapon}. ???????????? ?????????????? ?????????? ??????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'
                else:
                    return f'???????????????????? ?????????? {random_weapon}. ???????????? ?????????????? ?????????? ??????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 70 + hero_info['luck']:
                earn_money = hero_info['strength'] * 3 + hero_info['intellect'] + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??? ?????????????? ???????????? ???????????? ?????????????? ?????? ?????????????? ?? ?????????????? ??????????????. ' \
                       f'?????? ???????????????????? ???????????? ???????????? ?????????????????? ?? ?????????????? ??????????. ????????, ?????????? ???????????? ?????????? ?? ??????????????????.. ' + \
                       f'?????????????? ?????? ???? ??????????????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+3 ??????????'

            else:
                lost_money = chance % 10 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money}, exp={hero_info['exp'] + 4} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??????? ???????????????? ???? {random.randint(2, 4)} ????????. ' \
                       f'??? ?????? ???? ???????????? ?? ???????? ?????????????????????! ?? ?????? ?????? ???????????? ??????????????! ' \
                       f'[???????????? ???? ??????????????????]. ?????? ?????? ???????????? ???????????? ?????????????????? ?? ?????????? ????????????. ' \
                       f'?????????? ???????? ?? ???????????? ?????? ???????????? ??????????...' + '\n' + f'-{lost_money} ????????' + '\n' + '+4 ??????????'

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
                return '???? ??? ??????, ??????... ?????? ???? ??????????... ???????????? ?????????? ??????... ?????? ?????? ????????! ???????????? ????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 70 + hero_info['luck']:
                earn_money = hero_info['agility'] + hero_info['intellect'] * 2 + 20 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??? ???? ???????????? ?????????????????? ????????????, ???? ?? ?????????????? ??????????????????.. ' + '\n' + f'+{earn_money} ????????' + '\n' + '+3 ??????????'

            else:
                random_1 = ['??????????', '????????????????', '??????????', '??????????', '??????????', '??????????????', '????????']
                random_2 = ['????????????', '??????????????????', '??????????', '??????????', '??????????', '????????????????', '??????????']
                lost_money = chance % 10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'?????? ?????????????? {random.choice(random_1)} ?? {random.choice(random_2)}!???? ?????? ?????? ??????????! ' \
                       f'[???????????? ???? ??????????????????]. ' \
                       f'?????? ?????? ?????????????? ?????????????? ???????????? ?? ?????????? ????????????.' + '\n' + f'-{lost_money} ????????'

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
                return f'???? ?????????????? ???????? ???????? ??????????! ?????? ???????? ?????????????????????? ????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+2 ??????????'

            elif chance < 70 + hero_info['luck']:
                fell_tree = ['??????????', '??????', '??????????', '????????????', '??????????????????????', '????????']
                earn_money = hero_info['strength'] * 2 + hero_info['agility'] * 2 + 30 + chance // 10
                cursor.execute(f"UPDATE users SET money={user_money + earn_money}, exp={hero_info['exp'] + 3}, energy={0} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'??? ?????? ?????? ???? ?????????????? ?????????????? ????????... ' \
                       f'???????? ???? ???????????????? {random.choice(fell_tree)} ???? ?????????? ?????? ???? ????????. ' \
                       f'???????????????? ?????????????? ??????????????????.' + '\n' + f'+{earn_money} ????????' + '\n' + '+3 ??????????'

            else:
                lost_money = chance % 10 * 2 + 20
                cursor.execute(f"UPDATE users SET money={user_money - lost_money} "
                               f"WHERE user_id={user_id} ")
                connect.commit()
                return f'????????????????? ???? ?????????? ???? ?????????? ??????????????. ???????????????? ???????????????????? ????????????...' + '\n' + f'-{lost_money} ????????'

    finally:
        connect.close()
