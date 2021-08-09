from db.connection import get_connect


def get_classes_name(id_of_class):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if id_of_class == 'all':
                classes = []
                cursor.execute("SELECT name FROM classes ")
                row = cursor.fetchall()
                for hero_class in row:
                    classes.append(hero_class['name'])
                return classes
            else:
                cursor.execute(f"SELECT name FROM classes WHERE id={id_of_class}")
                name_of_class = cursor.fetchone()['name']
                return name_of_class
    except:
        connect.close()


def get_subclasses_name(user_id, all=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if all:
                classes = []

                cursor.execute(f"SELECT subclasses.name FROM users "
                               f"INNER JOIN subclasses ON users.class=subclasses.class WHERE user_id={user_id}")
                row = cursor.fetchall()
                for hero_subclass in row:
                    classes.append(hero_subclass['name'])
                return classes
            else:
                cursor.execute(f"SELECT subclasses.name FROM users "
                               f"INNER JOIN subclasses ON users.subclass=subclasses.id WHERE user_id={user_id}")
                name_of_subclass = cursor.fetchone()['name']
                return name_of_subclass

    except:
        connect.close()

