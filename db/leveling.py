from db.connection import get_connect


def new_lvl(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT exp, max_exp '
                           f'FROM users WHERE user_id={user_id}')
            hero_exp = cursor.fetchone()
            if hero_exp['exp'] >= hero_exp['max_exp']:
                return True
    except:
        pass
    finally:
        connect.close()


def lvl_up(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT lvl, max_exp, exp, upgrade_points '
                           f'FROM users WHERE user_id={user_id}')
            exp_info = cursor.fetchone()
            add_upgrade_points = exp_info['upgrade_points'] + 1
            new_lvl = exp_info['lvl']+1
            remaining_exp = exp_info['exp'] - exp_info['max_exp']
            new_max_exp = 7*new_lvl//5 + 10
            cursor.execute(f"UPDATE users SET lvl={new_lvl}, exp={remaining_exp}, max_exp={new_max_exp}, upgrade_points={add_upgrade_points} "
                           f"WHERE user_id={user_id}")
            connect.commit()
            return new_lvl

    finally:
        connect.close()


def add_exp(user_id, exp, with_mul=False):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if with_mul:
                cursor.execute(f'SELECT exp, exp_multiply '
                               f'FROM users WHERE user_id={user_id}')
                exp_info = cursor.fetchone()
                exp_multiply = exp_info['exp_multiply']
                new_exp = exp_info['exp'] + exp * exp_multiply
                cursor.execute(f"UPDATE users SET exp={new_exp} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return exp * exp_multiply
            else:
                cursor.execute(f'SELECT exp '
                               f'FROM users WHERE user_id={user_id}')
                exp_info = cursor.fetchone()
                new_exp = exp_info['exp'] + exp
                cursor.execute(f"UPDATE users SET exp={new_exp} "
                               f"WHERE user_id={user_id}")
                connect.commit()
                return exp
    finally:
        connect.close()