import random
import datetime
from db.connection import get_connect


def searching_or_not(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT is_searching_monsters FROM users "
                           f"WHERE user_id={user_id}")
            flag = cursor.fetchone()
            if flag['is_searching_monsters'] == 1:
                return True
            else:
                return False

    finally:
        connect.close()


def searching_monster(user_id, start_searching=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if start_searching:
                cursor.execute(f"UPDATE users SET is_searching_monsters=1 "
                               f"WHERE user_id={user_id}")
            else:
                cursor.execute(f"UPDATE users SET is_searching_monsters=0 "
                               f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def get_monsters(monster_name=None, for_contracts=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if for_contracts:
                cursor.execute(f"SELECT * FROM monsters WHERE in_dange=0 ")
                monsters = cursor.fetchall()
                return monsters
            else:
                cursor.execute(f"SELECT * FROM monsters "
                               f"WHERE name='{monster_name}' AND in_dange=0 ")
                monster = cursor.fetchone()
                return monster
    finally:
        connect.close()


def create_conversation_contracts(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            now = datetime.datetime.now()
            contract_recreate_time = now + datetime.timedelta(hours=1)
            contract_recreate_time = contract_recreate_time.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(f"SELECT * FROM monsters "
                           f"WHERE in_dange={0} ")
            monsters = cursor.fetchall()

            cursor.execute(f"SELECT * FROM conversation_contracts "
                           f"WHERE peer_id={peer_id} ")
            conversation_contracts = cursor.fetchall()
            random.shuffle(monsters)

            new_conversation_contracts = monsters[:9]

            if not conversation_contracts:
                for contract in new_conversation_contracts:
                    cursor.execute(f"INSERT INTO conversation_contracts(peer_id, monster_id, time_to_recreate) "
                                   f"VALUES ({peer_id}, {contract['id']}, '{contract_recreate_time}') ")
            else:
                cursor.execute(f"DELETE FROM conversation_contracts "
                               f"WHERE peer_id={peer_id} ")
                for contract in new_conversation_contracts:
                    cursor.execute(f"INSERT INTO conversation_contracts(peer_id, monster_id, time_to_recreate) "
                                   f"VALUES ({peer_id}, {contract['id']}, '{contract_recreate_time}') ")

            connect.commit()
    finally:
        connect.close()


def get_conversation_contracts(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT * FROM conversation_contracts "
                           f"INNER JOIN monsters ON conversation_contracts.monster_id=monsters.id WHERE peer_id={peer_id} AND is_completed=0 ")
            monsters = cursor.fetchall()
            return monsters
    finally:
        connect.close()


def get_time_to_recreate_contracts(peer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT time_to_recreate FROM conversation_contracts "
                           f"WHERE peer_id={peer_id}")

            try:
                time_from_db = cursor.fetchall()[0]['time_to_recreate']
            except:
                time_from_db = None

            if time_from_db != None:
                delta = time_from_db - datetime.datetime.now()
                seconds = delta.seconds
                days = delta.days
                if seconds > 3600 or days < 0:
                    now = datetime.datetime.now()
                    contract_recreate_time = now + datetime.timedelta(hours=1)
                    contract_recreate_time = contract_recreate_time.strftime('%Y-%m-%d %H:%M:%S')
                    cursor.execute(f"UPDATE conversation_contracts SET time_to_recreate='{contract_recreate_time}' "
                                   f"WHERE peer_id={peer_id} ")
                    connect.commit()
                    return True
                else:
                    return False

            else:
                return True

    finally:
        connect.close()


def complete_contract(peer_id, monster_name):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT id FROM monsters "
                           f"WHERE name='{monster_name}' ")
            monster_id = cursor.fetchone()['id']
            cursor.execute(f"UPDATE conversation_contracts SET is_completed={1} "
                           f"WHERE peer_id={peer_id} AND monster_id={monster_id} ")
            connect.commit()
    finally:
        connect.close()
        
        
def set_busy_contract(user_id, busy):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if busy:
                cursor.execute(f"UPDATE users SET contract_busy={1} "
                               f"WHERE user_id={user_id}")
                connect.commit()
            else:
                cursor.execute(f"UPDATE users SET contract_busy={0} "
                               f"WHERE user_id={user_id}")
                connect.commit()
    finally:
        connect.close()


def check_busy_contract(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT contract_busy FROM users "
                           f"WHERE user_id={user_id} ")
            return cursor.fetchone()['contract_busy']
    finally:
        connect.close()
