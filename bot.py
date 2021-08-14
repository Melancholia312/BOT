import math
import requests
import vk_api
from datetime import datetime
from collections import Counter
from time import strftime
from time import gmtime
from time import sleep
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard
from threading import *
from db.register import *
from db.menu import *
from db.get_classes import *
from db.dange import *
from db.hunt import *
from db.leveling import *
from db.auction import *
from db.items import *
from db.shop import *
from db.pvp import *
from db.racing import *
from db.events import *
from db.tavern import *
from db.fishing import *
from db.work import *
from db.revaral_system import *
from db.treasures import *
from db.admin import *
from gameplay.monsters import *
from gameplay.classes import *


vk = vk_api.VkApi(token="a44a2583217ac79dced23a0c9f5537c1c2d0c6d3a5d2108cd3cff8b18ad274913b4f839c6b5170e7a9779")
vk._auth_token()
vk.get_api()
group_id = 203434371
longpoll = VkBotLongPoll(vk, group_id)


def get_users_count(peer_id):
    return len(vk.method("messages.getConversationMembers", {"peer_id": peer_id})['items'])


def send_message(peer_id, text, keyboard=None, attachment=None):
    vk.method("messages.send", {"peer_id": peer_id, "message": text,
                                "random_id": random.randint(-9223372036854775807, 9223372036854775807),
                                "keyboard": keyboard,
                                "attachment": attachment})


def edit_message(peer_id, text, message_id):
    vk.method("messages.edit", {"peer_id": peer_id,
                                "message": text,
                                "conversation_message_id": message_id})


def delete_message(peer_id, message_id):
    vk.method("messages.delete", {"peer_id": peer_id,
                                  "conversation_message_ids": message_id,
                                  "delete_for_all": 1})


def create_keyboard(text, inline=True):
    if inline:
        keyboard = VkKeyboard(inline=True)
    else:
        keyboard = VkKeyboard(inline=False, one_time=False)
    count = 0
    for button in text:
        count += 1
        keyboard.add_button(button)
        if count % 3 == 0 and count != len(text):
            keyboard.add_line()
    return keyboard.get_keyboard()


def get_items_names(user_id=None, for_buttons=False, only_users_items=True):
    if only_users_items:
        list_with_items = get_user_inventory(user_id, False)
    else:
        list_with_items = get_all_items()
    item_names = []
    if for_buttons:
        for item in list_with_items:
            item_name_for_button = '/' + item['name']
            item_names.append(item_name_for_button)

    else:
        for item in list_with_items:
            item_name = item['name'].lower()
            item_names.append(item_name)
    return item_names


def monster_fight(player, monsters, peer_id, user_id, contract=False):
    step = 1
    log = ""
    if len(monsters) == 1:
        log = player.name + " атакует " + monsters[0].name + "!" + "\n"
    else:
        log = player.name + " атакует стаю чудовищ" + "!" + "\n"
        count_unit = 1
        for unit in monsters:
            log +="— "+ str(count_unit)+ "." + unit.name + \
                   " ♥ " + str(unit.health) + " 🛡 " + str(unit.armour) + "\n"
            count_unit+=1
    log += "\n"
    count_of_mnst = len(monsters)
    mnst_marker = list(range(0, count_of_mnst))
    while player.health > 0 and len(mnst_marker) > 0:
        log += str(step) + " ход. \n \n"
        log += player.name + " :"+" ♥ "+str(player.health) + " 🔷 " + str(player.mana) + \
               " 🛡 " + str(player.armour) + " 🗡 "+str(player.attack) + "\n"
        dead_list = []
        for ind_mnst in mnst_marker:

            if ind_mnst in dead_list:
                continue

            log += "~~~~~\n\n"

            log += player.name +" 🗡 ➡ " + str(ind_mnst+1)+"." +monsters[ind_mnst].name+". "+ "\n"
            next_act = tactic(player, monsters[ind_mnst])
            if next_act == 'm':
                log += player.active_ability(monsters[ind_mnst], monsters, [])
            elif next_act == 'd':
                log += player.defence()
            else:
                log += player.attack_to(monsters[ind_mnst])

            log += "\n"
            log += str(ind_mnst+1)+"." +monsters[ind_mnst].name + \
                   " :" + " ♥ " + str(monsters[ind_mnst].health) + \
                   " 🛡 " + str(monsters[ind_mnst].armour) + \
                   " 🗡 "+str(monsters[ind_mnst].attack) + "\n \n"
            if monsters[ind_mnst].health>0:
                log += str(ind_mnst+1)+"." + monsters[ind_mnst].name + " " + \
                       "🐾 ➡ " + player.name + "\n"

                if random.randint(0, 4) == 1:
                    log += monsters[ind_mnst].defence()
                else:
                    log += monsters[ind_mnst].attack_to(player)

                monsters[ind_mnst].post_fight()
            log += "\n"
            for i in mnst_marker:
                if monsters[i].health < 1 and not i in dead_list:
                    log += str(i + 1) + "." + monsters[i].name + " умирает... \n"
                    dead_list.append(i)

            log += "\n"

            player.post_fight()

        for i in dead_list:
            mnst_marker.remove(i)

        log += "~~~~~~~~~~~"+"*"*len(mnst_marker) + "\n"

        send_message(peer_id=peer_id, text=log)
        sleep(2)
        log = ""

        step += 1

        if step > 300:
            log += "Чудовища в страхе сбежали от " + player.name + "\n"
            break

    exp = 0
    money = 0
    alive = True
    if player.health > 0:
        log += player.name+" побеждает!"+"\n"
        exp = monsters[0].tier
        money = int(monsters[0].reward * player.money_bonus)
        if contract:
            complete_contract(peer_id, monsters[0].name)
        m_exp = add_exp(user_id, exp)
        m_money = add_money(user_id, money)
        log += "+"+str(m_exp) + " опыта" + "\n"
        log += "+"+str(m_money) + " крон" + "\n"
    else:
        alive = False
        log += "Чудовища одолели " + player.name + "..."+"\n"
        kill_or_heal_hero(user_id, True)

    send_message(peer_id=peer_id, text=log)
    return alive


def pvp_fight(user_id_a,user_id_b,peer_id):

    if random.randint(0,1)==1:
        user_id_a, user_id_b = user_id_b, user_id_a

    player_inf_a = get_stats(user_id_a)
    player_mult_a = get_stat_multiply(player_inf_a["class"])

    player_a = create_class(get_subclasses_name(user_id_a, False))
    player_a.get_state(player_inf_a, player_mult_a)

    player_inf_b = get_stats(user_id_b)
    player_mult_b = get_stat_multiply(player_inf_b["class"])

    player_b = create_class(get_subclasses_name(user_id_b, False))
    player_b.get_state(player_inf_b, player_mult_b)

    step = 1
    log = player_a.name + " атакует " + player_b.name + "!" + "\n"
    while player_a.health > 0 and player_b.health > 0:

        log += str(step) + " ход. \n \n"
        log += player_a.name + " :" + " ♥ " + str(player_a.health) + " 🔷 " + str(player_a.mana) + \
               " 🛡 " + str(player_a.armour) + " 🗡 " + str(player_a.attack) + "\n"

        next_act = tactic(player_a, player_b)

        if next_act == 'm':
            log += player_a.active_ability(player_b,[player_b], [])
        elif next_act == 'd':
            log += player_a.defence()
        else:
            log += player_a.attack_to(player_b)

        log +="\n"

        log += player_b.name + " :" + " ♥ " + str(player_b.health) + " 🔷 " + str(player_b.mana) + \
               " 🛡 " + str(player_b.armour) + " 🗡 " + str(player_b.attack) + "\n"
        if player_b.health <= 0 :
            send_message(peer_id=peer_id, text=log)
            log = ""
            break

        next_act = tactic(player_b, player_a)
        if next_act == 'm':
            log += player_b.active_ability(player_a, [player_a], [])
        elif next_act == 'd':
            log += player_b.defence()
        else:
            log += player_b.attack_to(player_a)

        player_a.post_fight()
        player_b.post_fight()

        log += "~~~~~~~~~~~" + "*" + "\n"

        send_message(peer_id=peer_id, text=log)
        sleep(2)
        step += 1
        log = ""
        if step > 30:
            break

    log = "Итог: \n"
    log += player_b.name + " :" + " ♥ " + str(player_b.health) + " 🔷 " + str(player_b.mana) + \
           " 🛡 " + str(player_b.armour) + " 🗡 " + str(player_b.attack) + "\n"
    log += player_a.name + " :" + " ♥ " + str(player_a.health) + " 🔷 " + str(player_a.mana) + \
           " 🛡 " + str(player_a.armour) + " 🗡 " + str(player_a.attack) + "\n\n"

    exp_a = step//2
    exp_b = step//2
    lvl_dif = player_a.lvl - player_b.lvl

    if player_a.health > player_b.health:
        kill_or_heal_hero(user_id_b, True)
        if lvl_dif < -3:
            exp_a *= lvl_dif*(-1)
        else:
            exp_a *= 2
        log += player_a.name + " побеждает!" + "\n"
        set_pvp_count(user_id_a, user_id_b, 1)
    else:
        kill_or_heal_hero(user_id_a, True)
        if lvl_dif > 3:
            exp_b *= lvl_dif*-1
        else:
            exp_b *= 2
        log += player_b.name + " побеждает!" + "\n"
        set_pvp_count(user_id_a, user_id_b, 2)

    m_exp_a = add_exp(user_id_a, exp_a)
    m_exp_b = add_exp(user_id_b, exp_b)

    log += player_a.name + "+" + str(m_exp_a) + " опыта. \n"
    log += player_b.name + "+" + str(m_exp_b) + " опыта."


    send_message(peer_id=peer_id, text=log)


def user_register(msg, user_id):

    if get_user_flag(user_id)['flag'] == 1:
        if msg in get_classes_name('all'):
            chose_class(user_id, msg)
            text_for_buttons = []
            for subclass in get_subclasses_name(user_id):
                text_for_buttons.append(subclass)
            text_for_buttons.append('Назад, я хочу изменить свой класс')
            set_flag(user_id, 2)
            msg_with_description = f'{description_for_class(user_id)}'
            send_message(user_id, msg_with_description, keyboard=create_keyboard(text_for_buttons))
        else:
            send_message(user_id, "Такого класса не сущесвует")

    elif msg.lower() == 'назад, я хочу изменить свой класс' and get_user_flag(user_id)['flag'] == 2:
        set_flag(user_id, 1)
        text_for_buttons = []
        for hero_class in get_classes_name('all'):
            text_for_buttons.append(hero_class)
        set_flag(user_id, 1)
        send_message(user_id, f"Выбери свой класс", keyboard=create_keyboard(text_for_buttons))

    elif get_user_flag(user_id)['flag'] == 2:
        if msg in get_subclasses_name(user_id):
            chose_subclass(user_id, msg)
            set_flag(user_id, 3)
            send_message(user_id, "Как будут звать твоего героя?")
        else:
            send_message(user_id, "Такого подкласса не сущесвует")

    elif get_user_flag(user_id)['flag'] == 3:

        if len(msg) > 50:
            send_message(user_id, "Никнейм должен быть не больше 50 символов")
        elif len(msg) < 3:
            send_message(user_id, "Никнейм должен быть больше 2 символов")
        else:
            chose_name(user_id, msg)
            set_flag(user_id, 4)
            send_message(user_id, "Введите код приглашения. Если его у вас нет, то просто введите - /")

    elif get_user_flag(user_id)['flag'] == 4:

        try:
            code = int(msg)
        except:
            code = None

        if msg == '/':
            own_referal_code = random.randint(100000, 999999)
            set_own_referal_code(user_id, own_referal_code)
            set_flag(user_id, 5)
            send_message(user_id, "Вы успешно зарегистрировались!", keyboard=create_keyboard(
                text=['/меню', '/помощь'], inline=False))

        elif code:

            try:
                inviter_id = check_invite(code)
            except:
                inviter_id = None

            if inviter_id:
                if not already_referal_or_not(user_id):
                    set_inviter(user_id, inviter_id)
                    own_referal_code = random.randint(100000, 999999)
                    set_own_referal_code(user_id, own_referal_code)
                    give_treasure(user_id, 1)
                    set_flag(user_id, 5)
                    send_message(user_id, "Вы успешно зарегистрировались!", keyboard=create_keyboard(
                        text=['/меню', '/помощь'], inline=False))

                    send_message(inviter_id, f'Ваш реферальный код был введен игроком @id{user_id}')
                    if count_referals(inviter_id) == 3:
                        give_treasure(inviter_id, 1)
                        send_message(inviter_id, f'За приглашение 3 рефералов вы получили Дорожный сундук!')
                    elif count_referals(inviter_id) == 6:
                        give_treasure(inviter_id, 5)
                        send_message(inviter_id, f'За приглашение 6 рефералов вы получили Бутылку с письмом!')
                    elif count_referals(inviter_id) == 9:
                        give_treasure(inviter_id, 2, 3)
                        send_message(inviter_id, f'За приглашение 9 рефералов вы получили 3 Зачарованных сундука!')
                    elif count_referals(inviter_id) == 14:
                        give_treasure(inviter_id, 4)
                        send_message(inviter_id, f'За приглашение 14 рефералов вы получили Потерянную шкатулку!')
                    elif count_referals(inviter_id) == 24:
                        give_treasure(inviter_id, 3)
                        send_message(inviter_id, f'За приглашение 3 рефералов вы получили Аукционный сундук!')

                else:
                    send_message(user_id, "Вы уже вводили код приглашения")
            else:
                send_message(user_id, "Такого кода приглашения не существует")
        else:
            send_message(user_id, "Введите корректный код приглашения")


def clear_msg(msg, command):
    lower_msg = msg.lower()
    if type(command) == list:
        for element in command:
            if element in lower_msg.split('/'):
                return True
    else:
        if command in lower_msg.split('/'):
            return True


def dange_stage_event(user_id, stage):
    alive = True
    chance = random.randint(0, 50)
    log = ''
    player_stats = get_stats(user_id)
    player_name = player_stats['name']
    money_reward = 0
    exp_reward = 0
    deep_limit = 25
    player_lvl = player_stats['lvl']
    rich_description = ["горшок с монетами",
                        "забытый кем-то кошелёк",
                        "скелет с монетой в зубах",
                        "горсть монет, откуда она здесь?",
                        "брошенный мешок"]
    sleep(1)
    if stage < 4 and chance < 10:
        log += player_name + ': ' + 'Здесь подозрительно тихо...' + '\n'
        send_message(peer_id=user_id, text=log)

    elif chance < 10 + player_stats['luck'] and stage % 2 == 0:
        log += player_name + ': ' + 'Сокровища!' + "\n"
        log += "Перед вами " + rich_description[chance % len(rich_description)] + ".\n"
        money_reward = chance * 2 + stage * 15
        money_reward = add_money(user_id, money_reward)
        log += "+" + str(money_reward) + ' Крон' + '\n'
        send_message(peer_id=user_id, text=log)

    elif chance < 26 - player_stats['luck'] and stage % 3 == 0:
        log += player_name + ': ' + 'Что сейчас произошло?' + "\n"
        drop_money = chance * stage // 2 * (-1)
        drop_money = add_money(user_id, drop_money)
        log += 'Вы видете как гоблин убегает вместе с вашим кошельком.' + '\n' + \
               str(drop_money) + ' Крон' + '\n'
        send_message(peer_id=user_id, text=log)

    elif chance < 40 - player_stats['luck'] and stage % 3 == 0:
        log += player_name + ': ' + 'Это ловушка!' + "\n"
        save_chance = random.randint(1, 100)
        if save_chance < 60 - player_stats['luck']:
            log += 'Вам удалось избежать ловушки и спуститься  ниже' + '\n'
        else:
            log += 'Вам не удалось спастись...' + '\n'
            kill_or_heal_hero(user_id, True)
            alive = False
        send_message(peer_id=user_id, text=log)

    elif stage % 3 == 0 and chance < 65 - player_stats['luck']:
        change_dange_floor(user_id)
        log += player_name + ': ' + 'Это место кажется мне знакомым...' + "\n"
        send_message(peer_id=user_id, text=log)

    else:
        dange_monsters = get_dangeon_mobs()
        target_tier = math.ceil(14 * stage / deep_limit)
        target_name = ''
        for mnst in dange_monsters:
            if mnst['tier'] == target_tier:
                target_name = mnst['name']
        log += player_name + ': ' + 'Зараза...' + "\n"
        send_message(peer_id=user_id, text=log)
        player_mult = get_stat_multiply(player_stats["class"])
        player = create_class(get_subclasses_name(user_id, False))
        player.get_state(player_stats, player_mult)
        monster_inf = get_dangeon_mobs(target_name, False)
        monster = generate_contract(player.lvl, monster_inf)
        alive = monster_fight(player, monster, user_id, user_id)

        if stage % 5 == 0 and stage > 0:
            if alive:
                log = player_name + ': ' + 'Та тварь явно охраняла что-то ценное...' + '\n'
                if check_full_inventory(user_id):
                    new_item = give_dange_item(user_id, stage)
                    log += 'Вы нашли ' + new_item
                    send_message(peer_id=user_id, text=log)
                else:
                    answer = 'Вы бы с радостью забрали ценную находку, но места в карманах нет...'
                    send_message(peer_id=user_id, text=answer)

    if not alive:
        exit_dange(user_id)
        answer = 'Вы вышли из данжа...'
        send_message(peer_id=user_id, text=answer)

    return alive


def dange_gameplay(msg, user_id, peer_id):
    if check_busy(user_id) == 0:
        if clear_msg(msg, ['левую', 'правую', 'центральную']):
                set_busy(user_id, True)
                dange_floor_before = check_dange_floor(user_id)

                if dange_stage_event(user_id, dange_floor_before):
                    next_stage(user_id)
                    dange_floor_after = check_dange_floor(user_id)
                    if dange_floor_after == check_dange_goal(user_id):
                        answer = 'Поздравляю, вы прошли'
                        exit_dange(user_id)
                        send_message(peer_id=user_id, text=answer)
                    else:
                        text_for_buttons = ['Левую', 'Центральную', 'Правую', '/выйти из данжа']
                        send_message(peer_id=user_id, text=f'Вы миновали {dange_floor_before} этаж. Куда пройдете дальше?',
                                     keyboard=create_keyboard(text_for_buttons))
                set_busy(user_id, False)

        elif clear_msg(msg, 'выйти из данжа'):
            answer = 'Вы вышли из данжа'
            exit_dange(user_id)
            send_message(peer_id=user_id, text=answer)

        elif clear_msg(msg, 'данж'):
            answer = 'Ты уже в данже'
            send_message(peer_id=peer_id, text=answer)

        elif '/' in msg:
            answer = 'Вы находитесь в данже!'
            send_message(peer_id=peer_id, text=answer)


def show_hero_info(user_info):
    space = '~~~~~~~~~~~~~' + " \n"
    hero_class_name = get_classes_name(user_info['class'])
    hero_subclass_name = get_subclasses_name(user_info['user_id'], False)
    show_case = 'Ваш ник:' + ' ' + user_info['name'] + '\n' + \
                'Уровень:' + ' ' + str(user_info['lvl']) + '\n' + \
                'Опыт:' + ' ' + f'{user_info["exp"]}/{user_info["max_exp"]}' + '\n' + \
                'Количество монет:' + ' ' + str(user_info['money']) + '\n' + \
                'Класс:' + ' ' + hero_class_name + '\n' + \
                'Подкласс:' + ' ' + hero_subclass_name + '\n'

    return space + show_case + space


def show_hero_status(user_info):
    text_for_buttons = []
    space = " \n" + '~~~~~~~~~~~~~' + " \n"
    if user_info['is_dead'] == 1:
        user_info['is_dead'] = 'Мертв☠'
        text_for_buttons.append('/Лекарь')
    else:
        user_info['is_dead'] = 'Жив❤'

    if user_info['in_expedition'] == 1:
        delta = user_info['expedition_time'] - datetime.datetime.now()
        seconds = delta.seconds
        days = delta.days
        if seconds > 3600 or days < 0:
            user_info['in_expedition'] = '⛵Ваш персонаж готов закончить экспедицию'
            text_for_buttons.append('/Закончить экспедицию')
        else:
            remaining_time = strftime("%H:%M", gmtime(seconds))
            user_info['in_expedition'] = f'⛵В экспедиции. До завершения осталось {remaining_time}'
    else:
        user_info['in_expedition'] = 'Не в экспедиции'
        text_for_buttons.append('/Экспедиция')

    if user_info['is_sleeping'] == 1:
        delta = user_info['sleep_time'] - datetime.datetime.now()
        seconds = delta.seconds
        days = delta.days
        if seconds > 10800 or days < 0:
            user_info['is_sleeping'] = '💤Выспался'
            text_for_buttons.append('/Разбудить персонажа')
        else:
            remaining_time = strftime("%H:%M", gmtime(seconds))
            user_info['is_sleeping'] = f'💤Спит. До пробуждения осталось {remaining_time}'
            text_for_buttons.append('/Досрочно разбудить персонажа')

    else:
        user_info['is_sleeping'] = 'Не спит'
        text_for_buttons.append('/Отдых')

    if user_info['on_job'] == 1:
        delta = user_info['end_job'] - datetime.datetime.now()
        seconds = delta.seconds
        days = delta.days
        if seconds > 7200 or days < 0:
            user_info['on_job'] = '⚒Ваш персонаж готов закончить работу'
            text_for_buttons.append('/Завершить работу')
        else:
            remaining_time = strftime("%H:%M", gmtime(seconds))
            user_info['on_job'] = f'⚒На работе. До завершения осталось {remaining_time}'
    else:
        user_info['on_job'] = 'Не на работе'
        text_for_buttons.append('/Работа')

    hero_status = 'Состояние персонажа:' + ' ' + user_info['is_dead'] + '\n' + \
                  '⚡Количество энергии:' + ' ' + f'{user_info["energy"]}/{user_info["max_energy"]}' + '\n' + \
                  user_info['is_sleeping'] + '\n' + \
                  user_info['in_expedition'] + '\n' + \
                  user_info['on_job']

    return {'answer': space + hero_status + space, 'text_for_buttons': text_for_buttons}


def show_hero_stats(hero_stats):
    space = '~~~~~~~~~~~~~' + " \n"
    hero_class_id = hero_stats['class']
    hero_name = hero_stats['name']
    stat_multiply = get_stat_multiply(hero_class_id)
    atk = str(hero_stats['ATK']) + ' + ' + str(hero_stats['strength'] * stat_multiply['multiply_strength_atk'] +
                                               hero_stats['agility'] * stat_multiply['multiply_agility_atk'] +
                                               hero_stats['intellect'] * stat_multiply['multiply_intellect_atk'])

    hp = str(hero_stats['HP']) + ' + ' + str(hero_stats['strength'] * stat_multiply['multiply_strength_hp'] +
                                             hero_stats['agility'] * stat_multiply['multiply_agility_hp'] +
                                             hero_stats['intellect'] * stat_multiply['multiply_intellect_hp'])

    mp = str(hero_stats['MP']) + ' + ' + str(hero_stats['strength'] * stat_multiply['multiply_strength_mp'] +
                                             hero_stats['agility'] * stat_multiply['multiply_agility_mp'] +
                                             hero_stats['intellect'] * stat_multiply['multiply_intellect_mp'])

    show_case = space + \
                "Ваши характеристики, " + hero_name + '.' + " \n" + \
                space + \
                "🗡Сила атаки:" + ' ' + str(atk) + " \n" + \
                "♥Количество ХП:" + ' ' + str(hp) + " \n" + \
                "🔷Количество МП:" + ' ' + str(mp) + " \n" + \
                "🥊Сила:" + ' ' + str(hero_stats['strength']) + " \n" + \
                "🥋Ловкость:" + ' ' + str(hero_stats['agility']) + " \n" + \
                "♟Интеллект:" + ' ' + str(hero_stats['intellect']) + " \n" + \
                "🀄Удача:" + ' ' + str(hero_stats['luck']) + " \n" + \
                space

    return show_case


def show_item_stats(item_stats):
    full_description = "Полное описание предмета" + " \n"
    space = '~~~~~~~~~~~~~' + " \n"
    show_case = "Название предмета:" + ' ' + item_stats['name'] + " \n" + \
                "Для класса:" + ' ' + str(get_item_class(item_stats['name'].title())) + " \n" + \
                "Разряд предмета:" + ' ' + str(item_stats['tier']) + " \n" + \
                "Слот предмета:" + ' ' + str(item_stats['slot']) + " \n"
    if item_stats['ATK'] != 0:
        show_case += "🗡Сила атаки:" + ' ' + str(item_stats['ATK']) + " \n"
    if item_stats['HP'] != 0:
        show_case += "♥Количество ХП:" + ' ' + str(item_stats['HP']) + " \n"
    if item_stats['MP'] != 0 :
        show_case += "🔷Количество МП:" + ' ' + str(item_stats['MP']) + " \n"
    if item_stats['strength'] != 0:
        show_case += "🥊Сила:" + ' ' + str(item_stats['strength']) + " \n"
    if item_stats['agility'] != 0:
        show_case += "🥋Ловкость:" + ' ' + str(item_stats['agility']) + " \n"
    if item_stats['intellect'] != 0:
        show_case += "♟Интеллект:" + ' ' + str(item_stats['intellect']) + " \n"
    if item_stats['luck'] != 0:
        show_case += "🀄Удача:" + ' ' + str(item_stats['luck']) + " \n"
    show_case += "Описание предмета:" + ' ' + item_stats['description'] + '\n'

    return full_description + space + show_case + space


def show_item_small_description(item_info):
    space = '~~~~~~~~~~~~~' + " \n"
    show_case = "Название предмета:" + ' ' + item_info['name'] + " \n" + \
                "Для класса:" + ' ' + str(get_item_class(item_info['name'].title())) + " \n" + \
                "Разряд предмета:" + ' ' + str(item_info['tier']) + " \n" + \
                "Слот предмета:" + ' ' + item_info['slot'] + " \n"

    return space + show_case + space


def zero_or_not(equip_info):
    if equip_info == 0:
        return 'Нет'
    else:
        return get_weapon_by_relation(equip_info)


def add_stats(item_stats, list_with_stats):
    if item_stats:
        list_with_stats['all_atk'] += item_stats['ATK']
        list_with_stats['all_hp'] += item_stats['HP']
        list_with_stats['all_mp'] += item_stats['MP']
        list_with_stats['all_strength'] += item_stats['strength']
        list_with_stats['all_agility'] += item_stats['agility']
        list_with_stats['all_intellect'] += item_stats['intellect']
        list_with_stats['all_luck'] += item_stats['luck']


def show_user_equipment(user_id):
    hero_info = get_hero_info(user_id)
    item_head_stats = get_weapon_by_relation(hero_info['item_head'], False)
    item_body_stats = get_weapon_by_relation(hero_info['item_body'], False)
    item_legs_stats = get_weapon_by_relation(hero_info['item_legs'], False)
    weapon_stats = get_weapon_by_relation(hero_info['weapon'], False)
    item_artifact_stats = get_weapon_by_relation(hero_info['item_artifact'], False)

    list_with_items_stats = [item_head_stats, item_body_stats, item_legs_stats, weapon_stats, item_artifact_stats]
    list_with_stats = {'all_atk': 0,
                       'all_hp': 0,
                       'all_mp': 0,
                       'all_strength': 0,
                       'all_agility': 0,
                       'all_intellect': 0,
                       'all_luck': 0}

    for item_stats in list_with_items_stats:
        add_stats(item_stats, list_with_stats)

    hero_slots = [zero_or_not(hero_info['item_head']),
                  zero_or_not(hero_info['item_body']),
                  zero_or_not(hero_info['item_legs']),
                  zero_or_not(hero_info['weapon']),
                  zero_or_not(hero_info['item_artifact'])]
    your_equipment = f"Ваше снаряжение, {hero_info['name']}" + " \n"
    space = '~~~~~~~~~~~~~' + " \n"
    show_case = "Голова:" + ' ' + hero_slots[0].title() + " \n" + \
                "Тело:" + ' ' + hero_slots[1].title()  + " \n" + \
                "Ноги:" + ' ' + hero_slots[2].title()  + " \n" + \
                "Оружие:" + ' ' + hero_slots[3].title()  + " \n" + \
                "Артефакт:" + ' ' + hero_slots[4].title()  + " \n"

    show_stats = ''
    show_msg_with_items = 'Статы, полученные от надетых вещей' + '\n'
    show_msg_without_items = 'На вас ничего не надето' + '\n'
    if list_with_stats['all_atk'] != 0:
        show_stats += "🗡Сила атаки:" + ' ' + str(list_with_stats['all_atk']) + " \n"
    if list_with_stats['all_hp'] != 0:
        show_stats += "♥Количество ХП:" + ' ' + str(list_with_stats['all_hp']) + " \n"
    if list_with_stats['all_mp'] != 0 :
        show_stats += "🔷Количество МП:" + ' ' + str(list_with_stats['all_mp']) + " \n"
    if list_with_stats['all_strength'] != 0:
        show_stats += "🥊Сила:" + ' ' + str(list_with_stats['all_strength']) + " \n"
    if list_with_stats['all_agility'] != 0:
        show_stats += "🥋Ловкость:" + ' ' + str(list_with_stats['all_agility']) + " \n"
    if list_with_stats['all_intellect'] != 0:
        show_stats += "♟Интеллект:" + ' ' + str(list_with_stats['all_intellect']) + " \n"
    if list_with_stats['all_luck'] != 0:
        show_stats += "🀄Удача:" + ' ' + str(list_with_stats['all_luck']) + " \n"

    text_for_buttons = []
    for item in hero_slots:
        if item != 'Нет':
            text_for_buttons.append(f'/снять {item}')
    if show_stats:
        return {'answer': your_equipment + space + show_case + space + show_msg_with_items + show_stats + space,
                'buttons': text_for_buttons}
    else:
        return {'answer': your_equipment + space + show_case + space + show_msg_without_items + space,
                'buttons': text_for_buttons}


def sliser(current_page, quantity, first=True):
    if first:
        return (current_page-1) * quantity
    else:
        return current_page * quantity


def create_auction_list(user_id, class_filter=False):
    quantity = 15
    text_for_buttons = []
    space = '~~~~~~~~~~~~~' + " \n"
    auction_offers_info = get_auction_offers(user_id, class_filter)
    if auction_offers_info:
        current_page = auction_offers_info["user_page"]
        offers = auction_offers_info['offers']
        offers.reverse()
        sliser_1 = sliser(current_page, quantity, True)
        sliser_2 = sliser(current_page, quantity, False)
        sliser_1_next = sliser(current_page+1, quantity, True)
        sliser_2_next = sliser(current_page+1, quantity, False)

        current_offers = offers[sliser_1:sliser_2]
        if current_offers:
            if current_page != 1:
                text_for_buttons.append('/Назад')

            if offers[sliser_1_next:sliser_2_next]:
                text_for_buttons.append('/Вперед')

            show_case = 'ID лота' + ' - ' + 'Название предмета' + ' - ' + 'Продавец' + ' - ' + 'Цена' + '\n' + space
            for offer in current_offers:
                show_case += str(offer['id']) + ' - ' + offer['name'] + ' - ' + f"@id{str(offer['seller_id'])}" + ' - ' + f'{str(offer["cost"])} крон' + '\n'
            show_current_page = f'Страница {current_page}'
            text_for_buttons.append('/мои лоты')
            return {'auction_list': space + show_case + space + show_current_page, 'buttons': text_for_buttons,
                    'current_page': current_page}
    else:
        return False


def create_user_auction_list(user_id):
    space = '~~~~~~~~~~~~~' + " \n"
    user_auction_info = get_user_offers(user_id)
    current_offers = user_auction_info['offers']
    max_auction_slots = user_auction_info['max_auction_slots']
    auction_slots = user_auction_info['auction_slots']
    if current_offers:
        show_case = f'Ваши лоты - {auction_slots}/{max_auction_slots}' + '\n' + 'ID лота' + ' - ' + 'Название предмета' + ' - ' + 'Продавец' + ' - ' + 'Цена' + '\n' + space
        for offer in current_offers:
            show_case += str(offer['id']) + ' - ' + offer['name'] + ' - ' + f"@id{str(offer['seller_id'])}" + ' - ' + str(offer['cost']) + '\n'
        return space + show_case + space
    else:
        return False


def show_magazine(user_id):
    space = '~~~~~~~~~~~~~' + " \n"
    shop_items = get_personal_shop_items(user_id)
    show_case = 'Магазин' + '\n' + space + 'ID предмета' + ' - ' + 'Название' + ' - ' + 'Цена' + '\n' + space
    text_for_buttons = []

    for item in shop_items:
        show_case += str(item['items.id']) + ' - ' + item['name'] + ' - ' + f'{str(item["cost"])} крон' + '\n'
        text_for_buttons.append(f'/{item["name"]}')
    text_for_buttons.append('/обновить магазин')
    show_case += space + '⚠ Обновление магазина стоит 500 крон!'
    return {'show_case': show_case, 'text_for_buttons': text_for_buttons}


def item_ids_from_shop(user_id):
    shop_items = get_personal_shop_items(user_id)
    item_names = []
    for item in shop_items:
        item_names.append(item['items.id'])
    return item_names


def race(all_racers, all_bet, peer_id):
    reward = 0
    all_racers = list(all_racers)

    count_of = len(all_racers)
    progress = [0 for i in range(count_of)]
    flag = True

    log = ""

    len_of_track = 35
    winner_name = []
    while flag:
        privilage = [3 for i in range(len(all_racers))]
        privilage[random.randint(0,len(all_racers)-1)] = 5
        for r in range(count_of):

            step = random.randint(privilage[r], privilage[r]+2)
            if step == 3:
                log += all_racers[r] + " споткнулся и упал !" + "\n"
            elif step == 6:
                step += 1
                log += "Что творит этот " + all_racers[r].title() + " !" + "\n"
            else:
                log += all_racers[r].title() + " :" + "\n"
            progress[r] += step

            if progress[r] >= len_of_track and flag:
                progress[r] = len_of_track
                winner_name.append(all_racers[r])
                flag = False

            log += '||' + '-' * (len_of_track - progress[r]) + '🏇' + \
                     "-" * progress[r] + "\n"
        log += "\n"
        send_message(peer_id, log)
        sleep(1)
        log = ''
    win_bet_count = {}

    
    win_bet_count[winner_name[0]] = 0
    log = "И наш победитель - " + winner_name[0].title() + '.' + "\n"
    win_bank = 0
    send_message(peer_id, log)
    log = ""
    for bt in all_bet:
        if not bt["racer_name"] in winner_name:
            reward += bt["bet"]
        else:
            win_bank += bt["bet"]
    for pl in all_bet:
        log += "@id" + str(pl["user_id"])

        if pl["racer_name"] in winner_name:
            calc_reward = pl["bet"] + int(reward*pl["bet"]/win_bank)
            add_money(pl["user_id"], calc_reward)
            log += " +" + str(calc_reward) + " крон \n"
        else:
            log += " -" + str(pl["bet"]) + " крон" + "\n"

    send_message(peer_id, log)


def show_contracts(peer_id):
    space = '~~~~~~~~~~~~~' + "\n"
    contracts = get_conversation_contracts(peer_id)
    show_case = '❗Доска с контрактами на монстров' + '\n' + space
    text_for_buttons = []
    emoji_for_tier = ['🐾',"🗿",'💀','👹','👻']
    if contracts:
        for contract in contracts:
            show_case += '☠' + contract['name'] + ' - ' + emoji_for_tier[contract["tier"]//5]+ '\n' + \
                          f'💰Вознаграждение {str(contract["reward_money"])} крон' + '\n' + space
            text_for_buttons.append(f'/напасть {contract["name"]}')
    else:
        show_case += 'Все контркаты выполнены. Ждите пока мы найдем новых чудовищ!'
    return {'show_case': space + show_case, 'text_for_buttons': text_for_buttons}


def show_tavern():
    space = '~~~~~~~~~~~~~' + "\n"
    drinks = get_drinks()
    text_for_buttons = []
    show_case = 'Название напитка - Цена - Эффект' + '\n' + space
    for drink in drinks:
        show_case += drink['name'] + ' - ' + f'{drink["cost"]} крон ' + f'+{drink["energy"]} энергии' + '\n' + space
        text_for_buttons.append(f'/выпить {drink["name"]}')
    return show_case, text_for_buttons


def show_fishing(user_id):
    space = '~~~~~~~~~~~~~' + "\n"
    text_for_buttons = []
    fishing_info = get_fishing_info(user_id)
    show_case = 'Меню рыбалки' + '\n' + space
    if fishing_info['fish_rod'] == 1:
        if fishing_info['fish_count'] > 0:
            text_for_buttons.append('/начать рыбалку')
            show_case += f'У вас есть удочка и вы можете рыбачить. Стоить это будет 1 энергию. Количество ваших попыток на сегодня - {fishing_info["fish_count"]}'
        else:
            user_fish_time = fishing_info['fish_time']
            delta = user_fish_time - datetime.datetime.now()
            seconds = delta.seconds
            remaining_time = strftime("%H:%M", gmtime(seconds))
            show_case += f'Сегодня вы нарыбачились сполна. Рыбалка будет доступна через {remaining_time}'

    else:
        text_for_buttons.append('/приобрести удочку')
        show_case += 'Купить удочку, чтобы рыбачить. Стоимость удочки - 260 крон'
    return show_case, text_for_buttons


def fishing(user_id, peer_id):
    user_info = get_hero_info(user_id)
    user_luck = user_info['luck']
    if user_luck < 0:
        user_luck = 0

    send_message(peer_id=peer_id, text='Рыбалка началась')
    sleep(2)
    send_message(peer_id=peer_id, text='Клюёт! 🐟')
    sleep(1)

    fish_chance = random.randint(1, 100)
    if fish_chance < 20 + user_luck:
        event = 2
    elif fish_chance < 50 + user_luck:
        event = 3
    elif fish_chance < 80 + user_luck:
        event = 1
    else:
        event = 4

    if event == 1:
        fish_sex = {'Плотва': 1, 'Карасик': 2, 'Окунь': 2, 'Язь': 2, 'Щука': 1, 'Карп': 2}
        fish = ['Плотва', 'Карасик', 'Окунь', 'Язь', 'Щука', 'Карп']
        random_fish = random.choice(fish)
        kg = random.randint(1, user_luck + 2)
        cost = random.randint(5, 5 + user_luck*2)*kg
        if fish_sex[random_fish] == 1:
            result = f'Вам попалась {random_fish} - {kg} кг!' + '\n' + f'На рынке за нее дадут {cost} крон'
        else:
            result = f'Вам попался {random_fish} - {kg} кг!' + '\n' + f'На рынке за него дадут {cost} крон'
        add_money(user_id, cost)
        send_message(peer_id=peer_id, text=result)

    elif event == 2:
        send_message(peer_id=peer_id, text='Тяжело идет...')
        chance = random.randint(0, user_luck + 1)
        if chance < 4:
            send_message(peer_id=peer_id, text='Ваша удочка сломалась...')
            brake_rode(user_id)
        elif chance < 11:
            if check_full_inventory(user_id):
                item_name = give_item(user_id, 1)
                send_message(peer_id=peer_id, text=f'Вы выловили {item_name}')
            else:
                answer = 'Валовленный вами предмет не поместился в рюкзаке и вы отдали его рыбаку, сидевшего рядом, за 50 крон'
                add_money(user_id, 50)
                send_message(peer_id=peer_id, text=answer)

        elif chance > 10:
            if check_full_inventory(user_id):
                item_name = give_item(user_id, 2)
                send_message(peer_id=peer_id, text=f'Вы выловили {item_name}')
            else:
                answer = 'Валовленный вами предмет не поместился в рюкзаке и вы отдали его рыбаку, сидевшего рядом, за 100 крон'
                add_money(user_id, 100)
                send_message(peer_id=peer_id, text=answer)

    elif event == 3:
        fish_phrases = ['Это опять ты, ублюдок?',
                        'Чего желаешь, красавчик?',
                        'Нет, нет, нет. Я не рассказываю анекдотов, даже если это часть желания',
                        'Тобой выбран неправильный пруд, клуб любителей рыбных изделий на две мили южнее',
                        'Предупреждаю, суккубы и прочие демоны не в моей компетенции!',
                        'Ну сколько ещё...',
                        'Ещё один...']
        send_message(peer_id=peer_id, text='Да это же Золотая Рыбка!' + '\n' + f'🐠:{random.choice(fish_phrases)}')

        if user_info['is_dead'] == 1:
            heal_phrases = ['🐠:Неудачный день? Ну что же... Все твои раны исцеленны!',
                            '🐠:Сильно тебя подрали... Надеюсь тебе это поможет. Vive, vive valeque!',
                            '🐠:Немного магии и теперь ты здоров! Но возможны небольшие побочные эффекты... Сыпь, рвота, понос и прочее.']
            kill_or_heal_hero(user_id, kill=False)
            send_message(peer_id=peer_id, text=random.choice(heal_phrases) + '\n' + 'Вас исцелили!')

        elif user_info['energy'] < 4:
            energy_phrases = ['🐠: Опять ходил по суккубам? Ну ладно, я ведь все-таки положительный персонаж.',
                              '🐠: Плохо выглядишь. Lorem ipsúm. Теперь лучше?',
                              '🐠: Ага, ага вот так, хорошо. Теперь можешь двигаться.']
            add_energy(user_id, 10)
            send_message(peer_id=peer_id, text=random.choice(energy_phrases) + '\n' + 'Ваша энергия полностью восстановлена ')

        else:
            money_phrases = ['🐠:Хочешь дворец, вечную жизнь? Или может быть виллу у моря? Ахахахахах' + '\n' + 'Вот держи!',
                             '🐠: Сегодня я в хорошем настроение. Так что держи.',
                             '🐠: Пам, пам, пам... На барабане сектор "Утешительный приз" !']
            money = add_money(user_id, random.randint(50, 150))
            send_message(peer_id=peer_id, text=random.choice(money_phrases) + '\n' + f'+{money} крон')

    else:
        send_message(peer_id=peer_id, text='Что это? Гнилой ботинок?')


def roulette(peer_id, user_id, user_color, bet):
    numbers = []
    for num in range(0, 37):
        numbers.append(num)
    win_num = random.choice(numbers)

    if win_num == 0:
        win_color = 'зеленое'
    elif win_num % 2 == 0:
        win_color = 'черное'
    elif win_num % 2 == 1:
        win_color = 'красное'

    sticker_color = {'черное': '🖤', 'красное': '❤', 'зеленое': '💚'}

    if user_color == win_color:
        if win_color in ['красное', 'черное']:
            win_money = add_money(user_id, bet)
            answer = f'Победное число {win_num} {win_color.title()}{sticker_color[win_color]}. Вы выиграли {win_money * 2} крон'
            send_message(peer_id=peer_id, text=answer)
        else:
            win_money = add_money(user_id, bet*13) + bet
            answer = f'Победное число {win_num} {win_color.title()}{sticker_color[win_color]}. Вы выиграли {win_money} крон'
            send_message(peer_id=peer_id, text=answer)
    else:
        add_money(user_id, -bet)
        answer = f'Победное число {win_num} {win_color.title()}{sticker_color[win_color]}. Вы проиграли {bet} крон'
        send_message(peer_id=peer_id, text=answer)


def show_jobs(user_id):
    space = '~~~~~~~~~~~~~' + " \n"
    jobs = get_personal_jobs(user_id)
    text_for_buttons = []
    if jobs:
        show_case = 'Работы' + '\n' + space

        for job in jobs:
            space = '~~~~~~~~~~~~~' + " \n"
            show_case += "Работа:" + ' ' + job['job_sticker'] + job['name'] + " \n"

            show_case += 'Требования по работе:' + '\n'
            if job['need_strength'] != 0:
                show_case += "🥊Сила:" + ' ' + str(job['need_strength']) + " \n"
            if job['need_agility'] != 0:
                show_case += "🥋Ловкость:" + ' ' + str(job['need_agility']) + " \n"
            if job['need_intellect'] != 0:
                show_case += "♟Интеллект:" + ' ' + str(job['need_intellect']) + " \n"
            if job['need_luck'] != 0:
                show_case += "🀄Удача:" + ' ' + str(job['need_luck']) + " \n"
            text_for_buttons.append(f'/работать {job["name"]}')
            show_case += space
        return {'show_case': show_case, 'text_for_buttons': text_for_buttons}
    else:
        return {'show_case': 'На сегодня больше вакансий нет', 'text_for_buttons': text_for_buttons}


def show_user_treasures(treasures):
    space = '~~~~~~~~~~~~~' + " \n"
    text_for_buttons = []
    show_case = 'Ваши сокровищницы' + '\n' + space
    show_case += 'Дорожный сундук: ' + str(treasures['treasure_1']) + '\n'
    show_case += 'Зачарованый сундук: ' + str(treasures['treasure_2']) + '\n'
    show_case += 'Аукционный сундук: ' + str(treasures['treasure_3']) + '\n'
    show_case += 'Потеряная шкатулка: ' + str(treasures['treasure_4']) + '\n'
    show_case += 'Бутылка с письмом: ' + str(treasures['treasure_5']) + '\n' + space

    if treasures['treasure_1'] != 0:
        text_for_buttons.append('/открыть дорожный сундук')

    if treasures['treasure_2'] != 0:
        text_for_buttons.append('/открыть зачарованый сундук')

    if treasures['treasure_3'] != 0:
        text_for_buttons.append('/открыть аукционный сундук')

    if treasures['treasure_4'] != 0:
        text_for_buttons.append('/открыть потеряная шкатулка')

    if treasures['treasure_5'] != 0:
        text_for_buttons.append('/открыть бутылка с письмом')

    return {'answer': show_case, 'text_for_buttons': text_for_buttons}

def index(msg, user_id, peer_id):

    if clear_msg(msg, 'регистрация') and not is_exists(user_id):
        try:
            text_for_buttons = []
            for hero_class in get_classes_name('all'):
                text_for_buttons.append(hero_class)
            send_message(peer_id=user_id, text=f"Выбери свой класс", keyboard=create_keyboard(text_for_buttons))
            register(user_id)
            set_flag(user_id, 1)
        except:
            send_message(peer_id=peer_id, text="Для регистрации нужно написать боту в личные сообщения "
                                                  "- https://vk.com/club203434371")
    elif clear_msg(msg, 'помощь'):
                space = "\n" + '~~~~~~~~~~~~~' + "\n"
                answer = "Полезные ссылки" + space + '📚Краткое руководство:' + '\n' +  'https://vk.com/topic-203434371_48149392' + '\n' + '🎯Советы для новых игроков:' + '\n' + 'https://vk.com/topic-203434371_48174280' + '\n' + \
                         '☎Исправление багов:' + '\n' +  'https://vk.com/topic-203434371_47471775' + \
                         '\n' + '\n' + 'По важным вопросам писать:' + '\n' + '🍰 [id276221064|@melancholia312]' + space
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text=['/меню', '/помощь'], inline=False))
    
    elif is_exists(user_id):
        
        if get_user_flag(user_id)['flag'] != 5:
            user_register(msg, user_id)

        elif check_dange_floor(user_id) > 0:
            dange_gameplay(msg, user_id, peer_id)           
    
        elif '/' in msg:

            if clear_msg(msg, 'точно удалить персонажа'):
                delete_hero(user_id)
                answer = "Да уж!"
                send_message(peer_id=peer_id, text=answer)       

            elif clear_msg(msg, 'меню'):
                text_for_buttons = ['/мой персонаж', '/магазин', '/аукцион',
                                    '/данж', '/контракты', '/рыбалка', '/таверна', '/скачки', '/рейтинг', '/реферальная система']
                answer = 'Меню'
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif clear_msg(msg, 'реферальная система'):
                text_for_buttons = ['/награды']
                space = "\n" + '~~~~~~~~~~~~~' + "\n"
                referal_key = get_user_referal_key(user_id)
                answer = 'Реферальная система' + space + 'Приглашайте своих друзей, чтобы получать награды!' + '\n' + \
                         f'Ваш код приглашения: {referal_key}' + space
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif clear_msg(msg, 'награды'):
                space = "\n" + '~~~~~~~~~~~~~' + "\n"
                referal_quantity = count_referals(user_id)
                answer = 'Награды' + space
                if referal_quantity >= 3:
                    answer += '❌ '
                else:
                    answer += '⭕ '
                answer += 'За 3 реферала вы получите Дорожный сундук' + '\n'
                if referal_quantity >= 6:
                    answer += '❌ '
                else:
                    answer += '⭕ '
                answer += 'За 6 рефералов вы получите Бутылку с письмом' + '\n'
                if referal_quantity >= 9:
                    answer += '❌ '
                else:
                    answer += '⭕ '
                answer += 'За 9 рефералов вы получите 3 Зачарованых сундука' + '\n'
                if referal_quantity >= 14:
                    answer += '❌ '
                else:
                    answer += '⭕ '
                answer += 'За 14 рефералов вы получите Потерянную шкатулку' + '\n'
                if referal_quantity >= 24:
                    answer += '❌ '
                else:
                    answer += '⭕ '
                answer += 'За 24 реферала вы получите Аукционный сундук' + '\n'
                answer += space + f'Количество ваших рефералов: {referal_quantity}'
                send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'время'):
                now_time = time.localtime()
                alt_year = str(now_time.tm_year - 1234)

                week_days = {
                    0: "Понедельник",
                    1: "Вторник",
                    2: "Среда",
                    3: "Четверг",
                    4: "Пятница",
                    5: "Суббота",
                    6: "Воскресенье",
                    7: "Понедельник"
                }
                months = {
                    1: "Января", 7: "Июля",
                    2: "Февраля", 8: "Августа",
                    3: "Марта", 9: "Сентебря",
                    4: "Апреля", 10: "Октября",
                    5: "Майя", 11: "Ноября",
                    6: "Июня", 12: "Декабря"
                }

                answer = str(now_time.tm_hour) + ':' + str(now_time.tm_min) + '\n' + \
                         week_days[now_time.tm_wday] + " " + months[now_time.tm_mon] + " " + \
                         alt_year + " года."
                send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'мой персонаж'):
                hero_info = get_hero_info(user_id)
                answer = show_hero_info(hero_info)
                text_for_buttons = ['/статы', '/мой инвентарь', '/мое снаряжение', '/дуэль инфо', '/состояние персонажа']
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons), attachment=hero_info['image'])

            elif clear_msg(msg, 'баланс'):
                hero_money = get_hero_info(user_id)['money']
                answer = f'Ваш баланс - {hero_money} крон'
                send_message(peer_id=peer_id, text=answer)
                
            elif clear_msg(msg, 'состояние персонажа'):
                hero_status = get_user_status(user_id)
                full_status_info = show_hero_status(hero_status)
                answer = full_status_info['answer']
                text_for_buttons = full_status_info['text_for_buttons']
                if text_for_buttons:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'разбудить персонажа'):
                if check_sleep(user_id):
                    user_sleep_time = get_user_status(user_id)['sleep_time']
                    delta = user_sleep_time - datetime.datetime.now()
                    seconds = delta.seconds
                    days = delta.days
                    if seconds > 10800 or days < 0:
                        wake_up(user_id)
                        answer = 'Выш персонаж отдохнул и полон сил'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        remaining_time = strftime("%H:%M", gmtime(seconds))
                        answer = f'Еще рано. До пробуждения осталось {remaining_time}'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Ваш персонаж не спит'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'досрочно разбудить персонажа'):
                if check_sleep(user_id):
                    wake_up(user_id, rest=False)
                    answer = 'Выш персонаж нисколько не отдохнул и чувствуется себя отвратительно'
                    send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Ваш персонаж не спит'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'закончить экспедицию'):
                if in_expedition(user_id):
                    user_expedition_time = get_user_status(user_id)['expedition_time']
                    delta = user_expedition_time - datetime.datetime.now()
                    seconds = delta.seconds
                    days = delta.days

                    if seconds > 3600 or days < 0:
                        answer = choose_event(user_id)
                        end_expedition(user_id)
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        remaining_time = strftime("%H:%M", gmtime(seconds))
                        answer = f'Еще рано. До конца экспедиции осталось {remaining_time}'
                        send_message(peer_id=peer_id, text=answer)

                else:
                    answer = 'Вы не ходили в экспедицию!'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'отдых'):
                if not check_sleep(user_id):
                    if not in_expedition(user_id):
                        if not is_working(user_id):
                            go_to_sleep(user_id)
                            answer = 'Ваш персонаж пошел отдыхать. Он будет готов вновь отправиться в бой через 3 часа'
                            send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = "Ваш персонаж работает"
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = "Ваш персонаж находится в экспедиции"
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Ваш персонаж и так отдыхает'
                    send_message(peer_id=peer_id, text=answer)

            elif 'дуэль инфо' in msg.lower():
                space = "\n" + '~~~~~~~~~~~~~' + "\n"
                pvp_info = check_pvp_stat(user_id)
                answer = 'Информация о ваших дуэлях' + space + \
                         f'Количество побед: {pvp_info["victory_count"]}' + '\n' + \
                         f'Количество поражений: {pvp_info["defeat_count"]}' + '\n'
                if pvp_info['enemy_id'] != 0:
                    if pvp_info['have_pvp_offer']:
                        answer += f'Вам бросил вызов игрок @id{pvp_info["enemy_id"]}' + space
                        text_for_buttons = ['/Дуэль принять', '/Дуэль отклонить']
                        send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        answer += f'Вы бросили вызов игроку @id{pvp_info["enemy_id"]}' + space
                        text_for_buttons = ['/Дуэль отозвать']
                        send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    answer += f'Вы не состоите в дуэли' + space
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'лекарь'):
                if not is_alive(user_id):
                    hero_info = get_hero_info(user_id)
                    user_money = hero_info['money']
                    cost = (hero_info['lvl']//3+1) * 75
                    if user_money >= cost:
                        add_money(user_id, -cost)
                        answer = f'Поздравляю! Вас отлично подлатали и вы готовы сражаться вновь! Вам это обошлось в {cost} крон'
                        kill_or_heal_hero(user_id, False)
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'У вас недостаточно средств'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Вы и так живее всех живых...'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'статы'):
                hero_stats = show_hero_stats(get_stats(user_id))
                text_for_buttons = ['/прокачка статов']
                send_message(peer_id=peer_id, text=hero_stats, keyboard=create_keyboard(text_for_buttons))

            elif clear_msg(msg, 'мой инвентарь'):
                text_for_buttons = ['/Предметы', '/Материалы', '/Сокровищницы']
                answer = 'Что вас интересует?'
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif clear_msg(msg, 'предметы'):
                hero_items = get_user_inventory(user_id, False)
                if hero_items:
                    text_for_buttons = get_items_names(user_id, True)
                    answer = 'Ваш инвентарь' + '\n'
                    for item in hero_items:
                        answer += show_item_small_description(item)
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    answer = 'Ваш инвентарь пуст'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'сокровищницы'):
                user_treasures = get_user_treasures(user_id)
                treasures_info = show_user_treasures(user_treasures)
                answer = treasures_info['answer']
                text_for_buttons = treasures_info['text_for_buttons']
                if text_for_buttons:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif '/открыть' in msg.lower():
                treasures_numbers = {'дорожный сундук': 1,
                                     'зачарованый сундук': 2,
                                     'аукционный сундук': 3,
                                     'потеряная шкатулка': 4,
                                     'бутылка с письмом': 5}
                try:
                    treausre_name = msg.split('/открыть')[1].lower().strip()
                except:
                    treausre_name = None

                if treausre_name:
                    if check_treasure_quantity(user_id, treasures_numbers[treausre_name]):
                        if check_full_inventory(user_id):
                            answer = open_treasure(user_id, treasures_numbers[treausre_name])
                            send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'У вас нет места в инвентаре'
                            send_message(peer_id=peer_id, text=answer)    
                    else:
                        answer = 'У вас нет этой сокровищницы'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Такой сокровищницы не существует'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'материалы'):
                answer = 'В разработке'
                send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'мое снаряжение'):
                user_equipment = show_user_equipment(user_id)
                answer = user_equipment['answer']
                if user_equipment['buttons']:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(user_equipment['buttons']))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, get_items_names(only_users_items=False)):
                item_name = msg.split('/')[1]
                item_stats = get_single_item_stat_by_name(item_name)
                answer = show_item_stats(item_stats)
                text_for_buttons = []
                hero_info = get_hero_info(user_id)

                list_with_equipment = [get_weapon_by_relation(hero_info['item_head']),
                                       get_weapon_by_relation(hero_info['item_body']),
                                       get_weapon_by_relation(hero_info['item_legs']),
                                       get_weapon_by_relation(hero_info['item_artifact']),
                                       get_weapon_by_relation(hero_info['weapon'])
                                       ]
                if item_name.lower() in list_with_equipment:
                    items_list = get_items_names(user_id, False)
                    count_item = Counter(items_list)
                    text_for_buttons.append(f'/снять {item_name.title()}')
                    if count_item[item_name.lower()] > 1:
                        text_for_buttons.append(f'/выкинуть {item_name.title()}')

                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

                elif item_name.lower() in get_items_names(user_id, False):
                    text_for_buttons.append(f'/надеть {item_name.title()}')
                    text_for_buttons.append(f'/выкинуть {item_name.title()}')
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'аукцион'):
                set_first_page(user_id)
                auction_info = create_auction_list(user_id)
                if auction_info:
                    answer = 'Аукцион' + '\n'
                    answer += auction_info['auction_list']
                    text_for_buttons = auction_info['buttons']
                    if text_for_buttons:
                        send_message(peer_id=user_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        send_message(peer_id=user_id, text=answer)
                else:
                    answer = 'Никто еще не выставлял вещи на аукцион.'
                    send_message(peer_id=user_id, text=answer)

            elif '/мои лоты' in msg.lower():
                set_first_page(user_id)
                auction_info = create_user_auction_list(user_id)
                if auction_info:
                    send_message(peer_id=user_id, text=auction_info)
                else:
                    answer = 'Вы ничего не выставляли на аукцион'
                    send_message(peer_id=user_id, text=answer)

            elif clear_msg(msg, 'вперед'):
                next_page(user_id, True)
                auction_info = create_auction_list(user_id)
                if auction_info:
                    text_for_buttons = auction_info['buttons']
                    delete_message(peer_id=user_id, message_id=get_message_id_for_auction(user_id))
                    answer = 'Аукцион' + '\n'
                    answer += auction_info['auction_list']
                    if text_for_buttons:
                        send_message(peer_id=user_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        send_message(peer_id=user_id, text=answer)
                else:
                    next_page(user_id, False)

            elif clear_msg(msg, 'назад'):
                next_page(user_id, False)
                auction_info = create_auction_list(user_id)
                if auction_info:
                    text_for_buttons = auction_info['buttons']
                    delete_message(peer_id=user_id, message_id=get_message_id_for_auction(user_id))
                    answer = 'Аукцион' + '\n'
                    answer += auction_info['auction_list']
                    if text_for_buttons:
                        send_message(peer_id=user_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        send_message(peer_id=user_id, text=answer)
                else:
                    next_page(user_id, True)

            elif '/выкупить' in msg.lower():
                try:
                    auction_id = int(msg.lower().split('/выкупить')[1].strip())
                except:
                    auction_id = None

                if auction_id in get_all_auction_ids(user_id):
                    if check_full_inventory(user_id):
                        buy_info = buy_item_auction(user_id, auction_id)
                        if buy_info:
                            seller_id = buy_info[1]
                            item_cost = buy_info[2]
                            offer_id = buy_info[3]
                            answer = 'Поздравляю с покупкой!'
                            send_message(peer_id=peer_id, text=answer)
                            seller_answer = f'У вас купили лот {offer_id} за {item_cost} монет!'
                            send_message(peer_id=seller_id, text=seller_answer)
                        else:
                            answer = 'У вас недостаточно средств'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'У вас нет места в инвентаре!'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Этого лота не существует или его невозможно купить'
                    send_message(peer_id=peer_id, text=answer)

            elif '/снять с продажи' in msg.lower():
                try:
                    auction_id = int(msg.split('/снять с продажи')[1][1:])
                except:
                    auction_id = None

                if auction_id in get_all_auction_ids(user_id, True):
                    drop_lot(user_id, auction_id)
                    answer = f'Вы сняли с продажи лот {auction_id}'
                    send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Вы не выставляли этот лот на продажу'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'прокачка статов'):
                points = get_upgrade_points(user_id)
                answer = f'У вас {points} очков прокачки. Что вы прокачаете?'
                text_for_buttons = ['/Силу', '/Ловкость', '/Интеллект']
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif clear_msg(msg, ['силу', 'ловкость', 'интеллект']):
                if get_upgrade_points(user_id) > 0:
                    stat_from_msg = msg.split('/')[1]
                    answer = f'Вы успешно прокачали {stat_from_msg}!'
                    if stat_from_msg.lower() == 'ловкость':
                        stat = 'agility'
                    elif stat_from_msg.lower() == 'силу':
                        stat = 'strength'
                    elif stat_from_msg.lower() == 'интеллект':
                        stat = 'intellect'
                    add_stat_point(user_id, stat)
                    send_message(peer_id=peer_id, text=answer)
                else:
                    answer = f'У вас недостаточно очков прокачки!!'
                    send_message(peer_id=peer_id, text=answer)

            elif '/надеть' in msg.lower():
                item_names = []
                for item in get_user_inventory(user_id, False):
                    item_names.append(item['name'].lower())
                if msg.lower().split('/надеть')[1][1:] in item_names:
                    item_name = msg.lower().split('/надеть')[1][1:]
                    if check_item_class(user_id, item_name):
                        if already_equip_or_not(user_id, item_name):
                            equip_item(user_id, item_name)
                            answer = f'Вы успешно надели {item_name.title()}'
                            send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Этот слот предмета уже занят!'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Этот предмет не предназначен для вашего класса'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Этого предмета нет у вас в инвентаре'
                    send_message(peer_id=peer_id, text=answer)

            elif '/снять' in msg.lower():
                item_names = []
                for item in get_user_inventory(user_id, False):
                    item_names.append(item['name'].lower())
                if msg.lower().split('/снять')[1][1:] in item_names:
                    item_name = msg.lower().split('/снять')[1][1:]
                    if not already_equip_or_not(user_id, item_name):
                        equip_item(user_id, item_name, False)
                        answer = f'Вы успешно сняли {item_name.title()}'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Вам нечего снимать...'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Этого предмета нет у вас в инвентаре'
                    send_message(peer_id=peer_id, text=answer)

            elif '/выкинуть' in msg.lower():
                item_names = []
                for item in get_user_inventory(user_id, False):
                    item_names.append(item['name'].lower())
                if msg.lower().split('/выкинуть')[1][1:] in item_names:
                    item_name = msg.lower().split('/выкинуть')[1][1:]
                    if drop_item(user_id, item_name):
                        answer = f'Вы выкинули {item_name.title()}'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = f'Вы не можете выкинуть этот предмет, так как он надет на вас'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Этого предмета нет у вас в инвентаре или его не существует'
                    send_message(peer_id=peer_id, text=answer)

            elif '/продать' in msg.lower():
                if '-' in msg:
                    item_names = []
                    for item in get_user_inventory(user_id, False):
                        item_names.append(item['name'].lower())
                    try:
                        item_info = msg.lower().split('/продать')[1].lower().strip().split('-')
                        item_name = item_info[0][:-1]
                        item_cost = int(item_info[1])
                        if item_cost > 10000000:
                            item_cost = None

                    except:
                        item_name = None
                        item_cost = None

                    if item_name in item_names:
                        if item_cost:
                            if full_auction_lots(user_id):
                                if sell_item(user_id, item_name, item_cost):
                                    answer = f'Вы успешно выставили {item_name.title()} на продажу за {item_cost}!'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = f'Вы не можете выкинуть этот предмет, так как он надет на вас'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = f'Вы выставили максимальное количество предметов на аукцион'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = f'Куда так цену загибаешь, друг?'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Этого предмета нет у вас в инвентаре или его не существует'
                        send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'магазин'):
                if get_time_to_recreate_shop(user_id):
                    create_personal_shop(user_id)
                shop_info = show_magazine(user_id)
                text_for_buttons = shop_info['text_for_buttons']
                answer = shop_info['show_case']
                if text_for_buttons:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif '/обновить магазин' in msg.lower():
                create_personal_shop(user_id)
                shop_info = show_magazine(user_id)
                text_for_buttons = shop_info['text_for_buttons']
                answer = shop_info['show_case']
                user_money = get_hero_info(user_id)['money']
                if user_money >= 500:
                    add_money(user_id, -500)
                    if text_for_buttons:
                        send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'У вас недостаточно средств'
                    send_message(peer_id=peer_id, text=answer)

            elif '/купить' in msg.lower():
                try:
                    item_id = int(msg.lower().split('/купить')[1].strip())
                except:
                    item_id = None

                if item_id in item_ids_from_shop(user_id):
                    if check_full_inventory(user_id):
                        if buy_item(user_id, item_id):
                            answer = 'Поздравляю с покупкой!'
                            send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'У вас недостаточно средств'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'У вас нет места в инвентаре!'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Этого предмета не существует или его невозможно купить'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'рейтинг'):
                answer = 'По каким критериям показать?'
                text_for_buttons = ['/рейтинг победы в дуэлях', '/рейтинг уровень',
                                    '/рейтинг количество крон']
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif '/рейтинг победы в дуэлях' in msg.lower():
                space = '~~~~~~~~~~~~~' + "\n"
                answer = 'Топ игроков по победам' + '\n' + space
                list_with_top_users = get_top_user_by_victory_count()
                count = 0
                for user in list_with_top_users:
                    count += 1
                    answer += f'№{str(count)}' + ' - ' + f'[id{user["user_id"]}|{user["name"]}]' + ' - ' \
                              + f'{str(user["victory_count"])} побед' + '\n'
                answer += space
                send_message(peer_id=peer_id, text=answer)

            elif '/рейтинг уровень' in msg.lower():
                space = '~~~~~~~~~~~~~' + "\n"
                answer = 'Топ игроков по уровню' + '\n' + space
                list_with_top_users = get_top_user_by_lvl()
                count = 0
                for user in list_with_top_users:
                    count += 1
                    answer += f'№{str(count)}' + ' - ' + f'[id{user["user_id"]}|{user["name"]}]' + ' - ' \
                              + f'{str(user["lvl"])} уровень' + '\n'
                answer += space
                send_message(peer_id=peer_id, text=answer)

            elif '/рейтинг количество крон' in msg.lower():
                space = '~~~~~~~~~~~~~' + "\n"
                answer = 'Топ игроков по количеству крон' + '\n' + space
                list_with_top_users = get_top_user_by_money()
                count = 0
                for user in list_with_top_users:
                    count += 1
                    answer += f'№{str(count)}' + ' - ' + f'[id{user["user_id"]}|{user["name"]}]' + ' - ' \
                              + f'{str(user["money"])} Крон' + '\n'
                answer += space
                send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'скачки'):
                if user_id != peer_id:
                    space = " \n" + '~~~~~~~~~~~~~' + " \n"
                    racers = {'летающая капуста': 0, 'волк одиночка': 0, 'ездовой ящер': 0}
                    max_bets = 2 + get_users_count(peer_id)//5
                    bets = get_all_bets(peer_id)
                    if bets:
                        answer = f'Начинается запись ставок ! {len(bets)}/{max_bets}' + space
                        for bet in bets:
                            racers[bet['racer_name']] += bet['bet']

                    else:
                        answer = 'В вашей беседе еще никто не делал ставок. Будьте первыми!' + space

                    count = 0
                    racers_names = 'Гонщики' + space
                    for racer in racers:
                        count += 1
                        racers_names += f'{str(count)}. ' + racer.title() + ' - ' + f'{str(racers[racer])} крон' + '\n'
                    send_message(peer_id=peer_id, text=answer + racers_names)

                else:
                    answer = 'Скачки доступны только в беседах'
                    send_message(peer_id=peer_id, text=answer)

            elif '/скачки ставка' in msg.lower():
                if user_id != peer_id:
                    racers = ['летающая капуста', 'волк одиночка',  'ездовой ящер']
                    try:
                        bet = int(msg.lower().split('/скачки ставка')[1].split('-')[1].strip())
                        racer_name = msg.lower().split('/скачки ставка')[1].split('-')[0].strip()
                    except:
                        bet = 0
                        racer_name = None

                    user_money = get_hero_info(user_id)['money']
                    if racer_name in racers:
                        if user_money >= bet:
                            if bet >= get_big_bet(peer_id):
                                bet_info = make_bet(user_id, bet, peer_id, racer_name)
                                if not bet_info:
                                    answer = 'Вы уже выбрали гонщика'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = bet_info
                                    bets = get_all_bets(peer_id)
                                    max_bets = 2 + get_users_count(peer_id)//5
                                    send_message(peer_id=peer_id, text=answer)
                                    if len(bets) == max_bets:
                                        answer = 'Гонка началась!'
                                        delete_all_bets(peer_id)
                                        send_message(peer_id=peer_id, text=answer)
                                        race(racers, bets, peer_id)
                            else:
                                answer = 'Вы не можете сделать такую маленькую ставку'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'У вас недостаточно средств'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Такого гонщика не существует!'
                        send_message(peer_id=peer_id, text=answer)

                else:
                    answer = 'Скачки доступны только в беседах'
                    send_message(peer_id=peer_id, text=answer)

            elif '/дуэль' in msg.lower():

                if '/дуэль принять' in msg.lower():
                    enemy_id = find_enemy(user_id)
                    if enemy_id:
                        if not check_sleep(user_id):
                            if is_alive(user_id):
                                if not in_expedition(user_id):
                                    if not is_working(user_id):
                                        pvp_fight(user_id, enemy_id, peer_id)
                                        drop_enemy_id(user_id, enemy_id)
                                    else:
                                        answer = "Ваш персонаж работает"
                                        send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = "Ваш персонаж находится в экспедиции"
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Ваш персонаж мертв!'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Ваш персонаж отдыхает!'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = f'Вас никто не вызывал на дуэль!'
                        send_message(peer_id=peer_id, text=answer)

                elif '/дуэль отклонить' in msg.lower():
                    enemy_id = find_enemy(user_id)
                    if enemy_id:
                        answer = f'Вы отклонили дуэль'
                        drop_enemy_id(user_id, enemy_id)
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = f'Вас никто не вызывал на дуэль!'
                        send_message(peer_id=peer_id, text=answer)

                elif '/дуэль отозвать' in msg.lower():
                    if check_enemy_id(user_id):
                        drop_enemy_id(user_id)
                        answer = 'Вы отозвали дуэль!'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Вы никого не вызывали на дуэль!'
                        send_message(peer_id=peer_id, text=answer)

                else:

                    try:
                        enemy_id = int(msg.lower().split('/дуэль')[1].strip().split('|')[0][3:])
                    except:
                        enemy_id = None

                    if enemy_id:
                        if is_exists(enemy_id):
                            if not check_enemy_id(user_id) and not find_enemy(user_id):
                                if enemy_id != user_id:
                                    if not check_sleep(user_id):
                                        if is_alive(enemy_id):
                                            if is_alive(user_id):
                                                if not in_expedition(user_id):
                                                    if not is_working(user_id):
                                                        choose_enemy(user_id, enemy_id)
                                                        answer = f'Вы бросили вызов игроку @id{enemy_id}'
                                                        text_for_buttons = ['/Дуэль принять', '/Дуэль отклонить']
                                                        send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                                                    else:
                                                        answer = "Ваш персонаж работает"
                                                        send_message(peer_id=peer_id, text=answer)
                                                else:
                                                    answer = "Ваш персонаж находится в экспедиции"
                                                    send_message(peer_id=peer_id, text=answer)
                                            else:
                                                answer = 'Ваш персонаж мертв!'
                                                send_message(peer_id=peer_id, text=answer)
                                        else:
                                            answer = 'Ты с трупом собрался сражаться?...'
                                            send_message(peer_id=peer_id, text=answer)
                                    else:
                                        answer = 'Ваш персонаж отдыхает!'
                                        send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = 'Ты больной?'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Вы уже учавствуете в дуэли!'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Данного пользователя не существует'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Данного пользователя не существует'
                        send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'данж'):
                if check_dange_floor(user_id) == 0:
                    if not check_sleep(user_id):
                        if is_alive(user_id):
                            if not in_expedition(user_id):
                                if not is_working(user_id):
                                    answer = 'Данж | Вы уверены? Поход в данж будет стоить вам 5 единицам энергии'
                                    text_for_buttons = ['/точно зайти в данж']
                                    send_message(peer_id=user_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                                else:
                                    answer = "Ваш персонаж работает"
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = "Ваш персонаж находится в экспедиции"
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Ваш персонаж мертв!'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Ваш персонаж отдыхает!'
                        send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'точно зайти в данж'):
                if check_dange_floor(user_id) == 0:
                    if not check_sleep(user_id):
                        if is_alive(user_id):
                            if not in_expedition(user_id):
                                if not is_working(user_id):
                                    if check_energy(user_id, 5):
                                        enter_dange(user_id)
                                        answer = f'Вы зашли в данж! В какую дверь пройдете?'
                                        text_for_buttons = ['Левую', 'Центральную', 'Правую', '/выйти из данжа']
                                        send_message(peer_id=user_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                                    else:
                                        answer = f'У вас не хватает энергии!'
                                        send_message(peer_id=user_id, text=answer)
                                else:
                                    answer = "Ваш персонаж работает"
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = "Ваш персонаж находится в экспедиции"
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Ваш персонаж мертв!'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Ваш персонаж отдыхает!'
                        send_message(peer_id=peer_id, text=answer)


            elif clear_msg(msg, 'контракты'):
                if user_id != peer_id:
                    if get_time_to_recreate_contracts(peer_id):
                        create_conversation_contracts(peer_id)
                    contracts_info = show_contracts(peer_id)
                    text_for_buttons = contracts_info['text_for_buttons']
                    answer = contracts_info['show_case']
                    if text_for_buttons:
                        send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                    else:
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Контракты доступны только в беседе'
                    send_message(peer_id=peer_id, text=answer)

            elif '/напасть' in msg.lower():
                if not check_sleep(user_id):
                    if is_alive(user_id):
                        if not in_expedition(user_id):
                            if not is_working(user_id):
                                list_with_monsters = get_conversation_contracts(peer_id)
                                monsters_name = []
                                for monster in list_with_monsters:
                                    monsters_name.append(monster['name'].lower())

                                target_name = msg.split('/напасть')[1].lower()[1:]

                                if target_name in monsters_name:
                                    if check_energy(user_id, 3):
                                        player_inf = get_stats(user_id)
                                        player_mult = get_stat_multiply(player_inf["class"])
    
                                        player = create_class(get_subclasses_name(user_id, False))
                                        player.get_state(player_inf, player_mult)
    
                                        monster_inf = get_monsters(target_name, False)
    
                                        monsters = generate_contract(player.lvl, monster_inf)
    
                                        alive = monster_fight(player, monsters, peer_id, user_id, contract=True)
                                        searching_monster(user_id, False)
                                    else:
                                        answer = f'У вас не хватает энергии!'
                                        send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = "Такого заказа не существует или же он вам не доступен"
                                    send_message(peer_id=peer_id, text=answer)
                                
                            else:
                                answer = "Ваш персонаж работает"
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = "Ваш персонаж находится в экспедиции"
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Ваш персонаж мертв!'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Ваш персонаж отдыхает!'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'экспедиция'):
                answer = 'Поход в экспедицию стоит 3 энергии. Вы уверены?'
                text_for_buttons = ['/отправиться в экспедицию']
                send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))

            elif '/отправиться в экспедицию' in msg.lower():
                if not check_sleep(user_id):
                    if is_alive(user_id):
                        if not in_expedition(user_id):
                            if not is_working(user_id):
                                if check_energy(user_id, 3):
                                    go_to_expedition(user_id)
                                    answer = 'Ваш персонаж отправился в экспедицию! Завершить ее вы сможете только через час'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = f'У вас не хватает энергии!'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = "Ваш персонаж работает"
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = "Ваш персонаж находится в экспедиции"
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Ваш персонаж мертв!'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Ваш персонаж отдыхает!'
                    send_message(peer_id=peer_id, text=answer)

            elif '/перевести кроны' in msg.lower():
                try:
                    recipient = int(msg.lower().split('/перевести кроны')[1].split('|')[0].strip()[3:])
                    value = int(msg.lower().split('/перевести кроны')[1].split('-')[-1].strip())
                except:
                    recipient = None
                    value = None

                user_money = get_hero_info(user_id)['money']
                if recipient:
                    if is_exists(recipient):
                        if value <= user_money:
                            if user_id != recipient:
                                send_money(user_id, recipient, value)
                                answer = f'Вы успешно перевели {value} крон игроку @id{recipient}'
                                send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Какой прок от этого?...'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'У вас недостаточно средств'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Такого игрока не существует'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Такого игрока не существует'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'таверна'):
                tip = ['Сегодня у нас пиво за пол цены!',
                       'Самое свежее молоко только у нас!',
                       'У нас есть отличный стейк из катоблепаса',
                       'Где-то я уже видел твоё лицо...',
                       'У меня есть новый анекдот !' + '\n' + 'Чернокнижнику приснилось, что он выиграл на скачках 5 тысяч крон, '
                                                              'но даже во сне он умудрился пропить эти деньги до того, как проснулся.' + '\n' + 'Не смешно? Уже слышал?',

                       'Хочешь историю ?' + '\n' + 'У меня есть один очень странный клиент, который каждый раз ничего не заказывает, а только спрашивает про новые анекдоты...',
                       'Анекдот!' + '\n' + 'Попали как-то на необитаемый остров странствуйщий рыцарь, чародейки-самоучка и чернокнижник...',
                       'Ещё один анекдот!' + '\n' + 'Чтобы перебить запах перегара от чернокнижника, попросите его разуться',
                       'Те наёмники за крайним столиком очень странно на тебя смотрят.',
                       'Когда я был таким же искателем приключений, но однажды орчья стрела пробила мне колено.',
                       'Вы бы плащ хотя-бы сняли...']
                tip_answer = 'Что будете пить? ' + random.choice(tip) + '\n' + '\n'
                answer, text_for_buttons = show_tavern()
                send_message(peer_id=peer_id, text= tip_answer + answer, keyboard=create_keyboard(text_for_buttons))

            elif '/выпить' in msg.lower():
                try:
                    drink = msg.lower().split('/выпить')[1].strip()
                except:
                    drink = None

                drink_info = get_drinks(by_name=True, name=drink)
                if drink_info:
                    user_money = get_hero_info(user_id)['money']
                    if user_money >= drink_info['cost']:
                        add_money(user_id, -drink_info['cost'])
                        add_energy(user_id, drink_info['energy'])
                        answer = f'Вы заплатили {drink_info["cost"]} крон и с удовольствием выпили {drink.title()}, восполнив {drink_info["energy"]} энергии!'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'У вас недостаточно средств'
                        send_message(peer_id=peer_id, text=answer)

                else:
                    answer = 'Такого напитка не сущетсвует'
                    send_message(peer_id=peer_id, text= answer)

            elif clear_msg(msg, 'рыбалка'):
                reset_fish_time(user_id)
                answer, text_for_buttons = show_fishing(user_id)
                if text_for_buttons:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'приобрести удочку'):
                if get_hero_info(user_id)['money'] >= 260:
                    if buy_fish_rod(user_id):
                        answer = 'Вы успешно приобрели удочку!'
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'У вас уже есть удочка'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'У вас недостаточно средств'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'начать рыбалку'):
                if get_fishing_info(user_id)['fish_rod'] == 1:
                    if check_fish_try(user_id):
                        if check_energy(user_id, 1):
                            fishing(user_id, peer_id)
                            spend_fish_count(user_id)
                        else:                    
                            answer = 'У вас недостаточно энергии'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Думаю, на сегодня хватит рыбалки'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'У вас нет удочки'
                    send_message(peer_id=peer_id, text=answer)

            elif '/рулетка' in msg.lower():

                try:
                    color = msg.lower().split('/рулетка')[1].strip().split('-')[0].strip().lower()
                except:
                    color = None
                try:
                    bet = int(msg.lower().split('/рулетка')[1].strip().split('-')[1].strip())
                except:
                    bet = None

                if color in ['красное', 'черное', 'зеленое']:
                    if bet:
                        if bet >= 5:
                            if bet <= get_hero_info(user_id)['money']:
                                roulette(peer_id, user_id, color, bet)
                            else:
                                answer = 'У вас недостаточно средств'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Минимальная ставка 5 крон!'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Вы указали некорректную ставку'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Такого цвета не существует'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'работа'):
                if get_time_to_recreate_jobs(user_id):
                    create_personal_list_jobs(user_id)
                jobs_info = show_jobs(user_id)
                text_for_buttons = jobs_info['text_for_buttons']
                answer = jobs_info['show_case']
                if text_for_buttons:
                    send_message(peer_id=peer_id, text=answer, keyboard=create_keyboard(text_for_buttons))
                else:
                    send_message(peer_id=peer_id, text=answer)

            elif '/работать' in msg.lower():

                try:
                    job_name = msg.lower().split('/работать')[1].strip()
                except:
                    job_name = None

                if get_time_to_recreate_jobs(user_id):
                    create_personal_list_jobs(user_id)

                current_job = get_job_by_name(user_id, job_name)
                job_id = current_job['job_id']

                if current_job:
                    hero_stats = get_stats(user_id)
                    if hero_stats['strength'] >= current_job['need_strength'] and hero_stats['agility'] >= current_job['need_agility'] and hero_stats['intellect'] >= current_job['need_intellect'] and hero_stats['luck'] >= current_job['need_luck']:
                        if is_alive(user_id):
                            if not in_expedition(user_id):
                                if not check_sleep(user_id):
                                    if not is_working(user_id):
                                        if check_energy(user_id, 2):
                                            go_to_job(user_id, job_id)
                                            answer = 'Вы отправились на работу. Рабочий день вы сможете закончить только через 2 часа'
                                            send_message(peer_id=peer_id, text=answer)
                                        else:
                                            answer = 'У вас недостаточно энергии'
                                            send_message(peer_id=peer_id, text=answer)
                                    else:
                                        answer = 'Вы уже на работе'
                                        send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = 'Ваш персонаж отдыхает'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Вы находитесь в экспедиции'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Как бы ты не хотел, но мертвым не поработаешь...'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Вы не подходите для этой вакансии!'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Такой вакансии не существует!'
                    send_message(peer_id=peer_id, text=answer)

            elif clear_msg(msg, 'завершить работу'):
                if is_working(user_id):
                    user_job_time = get_user_status(user_id)['end_job']
                    delta = user_job_time - datetime.datetime.now()
                    seconds = delta.seconds
                    days = delta.days

                    if seconds > 7200 or days < 0:
                        answer = choose_job_event(user_id)
                        end_job(user_id)
                        send_message(peer_id=peer_id, text=answer)
                    else:
                        remaining_time = strftime("%H:%M", gmtime(seconds))
                        answer = f'Еще рано. До конца работы осталось {remaining_time}'
                        send_message(peer_id=peer_id, text=answer)
                else:
                    answer = 'Вы не на работе'
                    send_message(peer_id=peer_id, text=answer)
                           
            elif clear_msg(msg, 'регистрация'):     
                answer = 'Вы уже зарегистрированы!'
                send_message(peer_id=peer_id, text=answer)    
            
            elif is_admin(user_id):

                if '/пополнить баланс' in msg.lower():

                    try:
                        recipient = int(msg.lower().split('/пополнить баланс')[1].split('|')[0].strip()[3:])
                        value = int(msg.lower().split('/пополнить баланс')[1].split('-')[-1].strip())
                    except:
                        recipient = None
                        value = None

                    if recipient:
                        if is_exists(recipient):
                            if user_id != recipient:
                                if value:
                                    add_money(recipient, value)
                                    answer = f'Вы успешно пополнили счет игрока @id{recipient} на {value} крон'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = 'Укажите валидное число крон!'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Какой прок от этого?...'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Такого игрока не существует'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Такого игрока не существует'
                        send_message(peer_id=peer_id, text=answer)

                elif '/добавить энергии' in msg.lower():

                    try:
                        recipient = int(msg.split('/добавить энергии')[1].split('|')[0].strip()[3:])
                        value = int(msg.split('/добавить энергии')[1].split('-')[-1].strip())
                    except:
                        recipient = None
                        value = None

                    if recipient:
                        if is_exists(recipient):
                            if user_id != recipient:
                                if value:
                                    add_energy(recipient, value)
                                    answer = f'Вы успешно пополнили энергию игрока @id{recipient} на {value}'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = 'Укажите валидное число энергии!'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Какой прок от этого?...'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Такого игрока не существует'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Такого игрока не существует'
                        send_message(peer_id=peer_id, text=answer)

                elif '/вручить сундук' in msg.lower():
                    
                    try:
                        recipient = int(msg.split('/вручить сундук')[1].split('|')[0].strip()[3:])
                        treasure_num = int(msg.split('/вручить сундук')[1].split('-')[-1].strip())
                    except:
                        recipient = None
                        treasure_num = None
                    
                    if recipient:
                        if is_exists(recipient):
                            if user_id != recipient:
                                if treasure_num in [1, 2, 3, 4, 5]:
                                    give_treasure(user_id, treasure_num)
                                    answer = f'Вы успешно дали игроку @id{recipient} сундук!'
                                    send_message(peer_id=peer_id, text=answer)
                                else:
                                    answer = 'Такого сундука не существует!'
                                    send_message(peer_id=peer_id, text=answer)
                            else:
                                answer = 'Какой прок от этого?...'
                                send_message(peer_id=peer_id, text=answer)
                        else:
                            answer = 'Такого игрока не существует'
                            send_message(peer_id=peer_id, text=answer)
                    else:
                        answer = 'Такого игрока не существует'
                        send_message(peer_id=peer_id, text=answer)
                    
            else:
                answer = 'Не суй свои ручонки :)'
                send_message(peer_id=peer_id, text=answer)

    elif not is_exists(user_id) and '/' in msg:
        answer = 'Вы не зарегистрированны!'
        send_message(peer_id=peer_id, text=answer)
    
    if new_lvl(user_id):
        answer = f'Поздравляю, вы достигли {lvl_up(user_id)} уровень!'
        send_message(peer_id=peer_id, text=answer)


def bot_side():
    if event.object['text'].startswith('Аукцион'):
        user_id = event.object['peer_id']
        message_id = event.object['conversation_message_id']
        add_message_id_for_auction(user_id=user_id, message_id=message_id)



while True:
    for event in longpoll.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW:
                Thread(target=index, args=(event.object['text'],
                                           event.object['from_id'],
                                           event.object['peer_id'],
                                           ), daemon=True).start()

            elif event.type == VkBotEventType.MESSAGE_REPLY:
                Thread(target=bot_side, daemon=True).start()

        except requests.exceptions.ReadTimeout:
            print('ConnectionError')
            continue

