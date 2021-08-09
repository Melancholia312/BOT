from db.connection import get_connect
dict_with_slots = {'Оружие': 'weapon', 'Голова': 'item_head', 'Тело': 'item_body',
                   'Ноги': 'item_legs', 'Артефакт': 'item_artifact'}


def add_message_id_for_auction(user_id, message_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET id_message_for_add_message_id_for_auction={message_id} "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def get_message_id_for_auction(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT id_message_for_add_message_id_for_auction FROM users "
                           f"WHERE user_id={user_id}")
            message_id = cursor.fetchone()['id_message_for_add_message_id_for_auction']
            return message_id
    finally:
        connect.close()


def get_auction_offers(user_id, class_filter):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT class, auction_page FROM users "
                           f"WHERE user_id={user_id} ")
            user_info = cursor.fetchone()
            user_page = user_info['auction_page']
            if class_filter:
                user_class = user_info['class']
                cursor.execute(f"SELECT * FROM auction "
                               f"INNER JOIN items ON auction.item=items.id WHERE class={user_class}")
            else:
                cursor.execute(f"SELECT * FROM auction "
                               f"INNER JOIN items ON auction.item=items.id WHERE NOT seller_id={user_id} ")
            offers = cursor.fetchall()
            if offers:
                return {'offers': offers, 'user_page': user_page}
            else:
                return False
    finally:
        connect.close()


def get_user_offers(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT auction_slots FROM users "
                           f"WHERE user_id={user_id} ")
            max_auction_slots = cursor.fetchone()['auction_slots']
            cursor.execute(f"SELECT * FROM auction "
                           f"WHERE seller_id={user_id} ")
            auction_slots = len(cursor.fetchall())
            cursor.execute(f"SELECT * FROM auction "
                           f"INNER JOIN items ON auction.item=items.id WHERE seller_id={user_id}")
            offers = cursor.fetchall()
            return {'offers': offers, 'max_auction_slots': max_auction_slots,
                    'auction_slots': auction_slots}
    finally:
        connect.close()


def next_page(user_id, next=True):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT auction_page FROM users WHERE user_id={user_id}")
            if next:
                next_auction_page = cursor.fetchone()['auction_page'] + 1
            else:
                next_auction_page = cursor.fetchone()['auction_page'] - 1
            cursor.execute(f"UPDATE users SET auction_page={next_auction_page} "
                           f"WHERE user_id={user_id}")
            connect.commit()
            return next_auction_page
    finally:
        connect.close()


def set_first_page(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"UPDATE users SET auction_page=1 "
                           f"WHERE user_id={user_id}")
            connect.commit()
    finally:
        connect.close()


def get_all_auction_ids(user_id, user_offers=False):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            if not user_offers:
                cursor.execute(f"SELECT id FROM auction WHERE NOT seller_id={user_id} ")
                offers = cursor.fetchall()
                offers_ids = []
                for offer in offers:
                    offers_ids.append(offer['id'])
                return offers_ids
            else:
                cursor.execute(f"SELECT id FROM auction WHERE seller_id={user_id} ")
                offers = cursor.fetchall()
                offers_ids = []
                for offer in offers:
                    offers_ids.append(offer['id'])
                return offers_ids
    finally:
        connect.close()


def buy_item_auction(user_id, offer_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT money FROM users "
                           f"WHERE user_id={user_id} ")
            hero_money = cursor.fetchone()['money']
            cursor.execute(f"SELECT cost, seller_id, item FROM auction "
                           f"WHERE id={offer_id} ")
            offer_info = cursor.fetchone()
            seller_id = offer_info['seller_id']
            item_cost = offer_info['cost']
            item_id = offer_info['item']

            if item_cost <= hero_money:
                new_hero_money = hero_money - item_cost
                cursor.execute(f"UPDATE users SET money={new_hero_money} "
                               f"WHERE user_id={user_id}")
                cursor.execute(f"SELECT money FROM users "
                               f"WHERE user_id={seller_id} ")
                seller_money = cursor.fetchone()['money']
                new_seller_money = seller_money + item_cost
                cursor.execute(f"UPDATE users SET money={new_seller_money} "
                               f"WHERE user_id={seller_id}")
                cursor.execute(f"DELETE FROM auction "
                               f"WHERE id={offer_id} ")
                cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                               f"VALUES ({user_id}, {item_id}) ")
                connect.commit()
                return True, seller_id, item_cost, offer_id
            else:
                return False
    finally:
        connect.close()


def sell_item(user_id, item_name, item_cost):
    connect = get_connect()

    try:
        with connect.cursor() as cursor:
            cursor.execute(f'SELECT id, slot '
                           f'FROM items WHERE name="{item_name}"')
            item_info = cursor.fetchone()
            item_id = item_info['id']
            item_slot = dict_with_slots[item_info['slot']]
            cursor.execute(f'SELECT id FROM `relation_items_users` '
                           f'WHERE user_id={user_id} AND item_id={item_id} ')
            relation_id = cursor.fetchall()
            if len(relation_id) > 1:
                relation_id = relation_id[-1]['id']
            else:
                relation_id = relation_id[0]['id']

            cursor.execute(f'SELECT {item_slot} '
                           f'FROM users WHERE user_id={user_id}')
            hero_item_slot_id = cursor.fetchone()[item_slot]
            if relation_id == hero_item_slot_id:
                return False
            else:
                cursor.execute(f"INSERT INTO auction(seller_id, item, cost) "
                               f"VALUES ({user_id}, {item_id}, {item_cost}) ")
                cursor.execute(f'DELETE FROM relation_items_users '
                               f'WHERE user_id={user_id} AND id={relation_id} LIMIT 1 ')
                connect.commit()
                return True
    finally:
        connect.close()


def full_auction_lots(user_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT auction_slots FROM users "
                           f"WHERE user_id={user_id} ")
            max_slots = cursor.fetchone()['auction_slots']
            cursor.execute(f"SELECT * FROM auction "
                           f"WHERE seller_id={user_id} ")
            user_items = cursor.fetchall()
            if len(user_items) < max_slots:
                return True
            return False
    finally:
        connect.close()


def drop_lot(user_id, auction_id):
    connect = get_connect()
    try:
        with connect.cursor() as cursor:
            cursor.execute(f"SELECT item FROM auction "
                           f"WHERE id={auction_id} ")
            item_id = cursor.fetchone()['item']
            cursor.execute(f"INSERT INTO relation_items_users(user_id, item_id) "
                           f"VALUES ({user_id}, {item_id}) ")
            cursor.execute(f"DELETE FROM auction WHERE seller_id={user_id} AND id={auction_id} ")
            connect.commit()
    finally:
        connect.close()