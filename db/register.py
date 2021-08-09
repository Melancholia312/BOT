from db.connection import get_connect


def is_exists(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            result = cursor.execute(f'SELECT id FROM users WHERE user_id={user_id}')
            if result == 1:
                return True
            return False
    finally:
        connect.close()


def get_user_flag(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT flag FROM users WHERE user_id={user_id}')
            flag = cursor.fetchone()
            return flag

    finally:
        connect.close()


def register(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"INSERT INTO users(user_id) VALUES({user_id})")
            connect.commit()

    finally:
        connect.close()


def set_flag(user_id, num):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET flag={num} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def chose_class(user_id, hero_class):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT id FROM classes WHERE name='{hero_class}' ")
            id_of_hero_class = cursor.fetchone()
            cursor.execute(f"UPDATE users SET class={id_of_hero_class['id']} "
                           f"WHERE user_id={user_id}")

            connect.commit()

    finally:
        connect.close()


def chose_subclass(user_id, hero_subclass):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT id FROM subclasses WHERE name='{hero_subclass}' ")
            id_of_hero_subclass = cursor.fetchone()
            cursor.execute(f"UPDATE users SET subclass={id_of_hero_subclass['id']} "
                           f"WHERE user_id={user_id}")

            connect.commit()

    finally:
        connect.close()


def description_for_class(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:

            cursor.execute(f"SELECT description FROM users "
                           f"INNER JOIN classes ON users.class=classes.id WHERE user_id={user_id}")
            class_description = cursor.fetchone()
            return class_description['description']

    finally:
        connect.close()


def chose_name(user_id, name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET name='{name}' "
                           f"WHERE user_id={user_id}")
            cursor.execute(f"SELECT * FROM users "
                           f"INNER JOIN subclasses ON users.subclass=subclasses.id WHERE user_id={user_id}")
            full_hero_info = cursor.fetchone()
            cursor.execute(f"UPDATE users SET HP={full_hero_info['subclasses.HP']}, "
                           f"MP={full_hero_info['subclasses.MP']}, "
                           f"ATK={full_hero_info['subclasses.ATK']}, "
                           f"strength={full_hero_info['subclasses.strength']}, "
                           f"agility={full_hero_info['subclasses.agility']}, "
                           f"intellect={full_hero_info['subclasses.intellect']}, "
                           f"luck={full_hero_info['subclasses.luck']}, "
                           f"CRIT_RATE={full_hero_info['subclasses.CRIT_RATE']}, "
                           f"image='{full_hero_info['subclasses.image']}' "
                           f"WHERE user_id={user_id}")

            connect.commit()

    finally:
        connect.close()


def delete_hero(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f'DELETE FROM users WHERE user_id={user_id}')
            connect.commit()
    finally:
        connect.close()



