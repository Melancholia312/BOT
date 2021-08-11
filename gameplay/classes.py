import random
import time

random.seed()


class Character:
    name = "kesha"
    class_id = 0
    lvl = 1
    strength = 5
    agility = 6
    intelligence = 4
    max_health = 800
    max_mana = 500
    health = 80
    mana = 50
    attack = 100
    crit_rate = 3
    armour = 100
    max_armour = 100
    luck = 5
    cast_cost = 40
    good_effect_hp = 3
    good_effect_mp = 3
    bad_effect_hp = 0
    bad_effect_mp = 0
    money_bonus = 1
    active_ability = None
    passive_ability = None
    multiply_strength_atk = 3
    multiply_intellect_atk = 0
    multiply_agility_atk = 2
    multiply_strength_hp = 5
    multiply_agility_hp = 2
    multiply_intellect_hp = 0
    multiply_strength_mp = 0
    multiply_agility_mp = 1
    multiply_intellect_mp = 2
    max_attack = 10
    ability_type = 'd'
    mana_used = 0
    armour_safe = 50
    health_safe = 60
    start_flag = True

    def attack_to(self, enemy):
        if self.luck > 20:
            self.luck = 20

        atc_log = ""
        chance = random.randint(1, 100)

        calc_damage = self.attack
        if chance < self.crit_rate + self.luck // 2:
            crit_bonus = (chance / 100 + 1.2)
            if crit_bonus > 1.5:
                crit_bonus = 1.5
            calc_damage = int(calc_damage * crit_bonus)
            
            atc_log += self.name + " наносит критический урон! " + "-" + str(calc_damage) + " \n"

        elif chance < 80 + self.luck:
            
            base_bonus = chance / 100 + 0.2
            
            if base_bonus > 1:
                base_bonus = 1
                
            calc_damage = int(calc_damage*base_bonus)
            
            atc_log += self.name + " наносит " + str(calc_damage) + " единиц урона!" + " \n"

        elif chance < 90 + self.luck:
            calc_damage = 0
            atc_log += self.name + " промахивается." + "\n"

        else:
            self.health -= calc_damage // 4
            atc_log += "Оружие выскальзывает из рук " + self.name + " и вонзается в ногу! -" + str(
                calc_damage // 4) + " \n"
            calc_damage = 0

        if chance % 17 == 0:
            calc_bad_effect = int(enemy.health / 100 * 5) + 5
            atc_log += "Кровотечение у " + enemy.name + '.' + "\n" + \
                       '-' + str(calc_bad_effect) + " hp/sec" + "\n"
            enemy.bad_effect_hp += calc_bad_effect

        calc_damage_armour = calc_damage - enemy.armour * 2
        enemy.armour -= int(calc_damage * 0.15)
        calc_damage = calc_damage_armour

        if calc_damage < 0:
            calc_damage = 0
        if enemy.armour < 0:
            enemy.armour = 0

        enemy.health -= calc_damage

        return atc_log

    def defence(self):

        extra_armour = self.max_armour // 3 + random.randint(self.luck, self.luck + 5)
        if self.armour + extra_armour <= int(self.max_armour * 1.1):
            self.armour += extra_armour
            def_log = self.name + " готовится к защите! \n +" + str(extra_armour) + "🛡" + "\n"
        else:
            self.armour = int(self.max_armour * 1.1)
            def_log = self.name + " готовится к защите! \n " + str(self.armour) + "🛡" + "\n"
        return def_log

    def post_fight(self):

        if self.health + self.good_effect_hp <= self.max_health:
            self.health += self.good_effect_hp
        if self.mana + self.good_effect_mp <= self.max_mana:
            self.mana += self.good_effect_mp

        self.passive_ability()

        self.health -= self.bad_effect_hp
        self.mana -= self.bad_effect_mp

        if self.bad_effect_hp > 0:
            self.bad_effect_hp //= 4
        else:
            self.bad_effect_hp = 0

    def valid_state(self):
        if self.health > 0:
            return True
        else:
            return False
        pass

    def get_state(self, stats_from_bd, multiply_from_bd):

        self.name = stats_from_bd['name']
        self.health = stats_from_bd['HP']
        self.mana = stats_from_bd['MP']
        self.attack = stats_from_bd['ATK']
        self.lvl = stats_from_bd['lvl']
        self.strength = stats_from_bd['strength']
        self.agility = stats_from_bd['agility']
        self.intelligence = stats_from_bd['intellect']
        self.crit_rate = stats_from_bd['CRIT_RATE']
        self.multiply_strength_atk = multiply_from_bd['multiply_strength_atk']
        self.multiply_intellect_atk = multiply_from_bd['multiply_intellect_atk']
        self.multiply_agility_atk = multiply_from_bd['multiply_agility_atk']
        self.multiply_strength_hp = multiply_from_bd['multiply_strength_hp']
        self.multiply_agility_hp = multiply_from_bd['multiply_agility_hp']
        self.multiply_intellect_hp = multiply_from_bd['multiply_intellect_hp']
        self.multiply_strength_mp = multiply_from_bd['multiply_strength_mp']
        self.multiply_agility_mp = multiply_from_bd['multiply_agility_mp']
        self.multiply_intellect_mp = multiply_from_bd['multiply_intellect_mp']
        self.luck = stats_from_bd['luck']

        self.max_health = self.health + \
                          self.strength * self.multiply_strength_hp + \
                          self.agility * self.multiply_agility_hp + \
                          self.intelligence * self.multiply_intellect_hp
        self.max_mana = self.mana + \
                        self.strength * self.multiply_strength_mp + \
                        self.agility * self.multiply_agility_mp + \
                        self.intelligence * self.multiply_intellect_mp
        self.attack = self.attack + \
                      self.strength * self.multiply_strength_atk + \
                      self.agility * self.multiply_agility_atk + \
                      self.intelligence * self.multiply_intellect_atk

        self.health = self.max_health
        self.health_safe = self.max_health // 5
        self.mana = self.max_mana
        self.armour = self.agility * self.multiply_strength_atk // 2 + self.strength
        self.armour_safe = self.armour // 2
        self.max_armour = self.armour
        self.max_attack = self.attack
        self.passive_ability()


class Knight(Character):

    def round_attack(self, all_enemies):
        for enemy in all_enemies:
            enemy.health -= int(self.attack / 4 * 3)
        self.mana -= self.cast_cost
        return self.name + " использует круговую атаку! \n -" + str(self.cast_cost) + "🔷" + "\n"

    def the_will_for_life(self):
        if self.health < self.max_health / 100 * 30:
            self.armour += self.armour_safe
            self.armour_safe = 0

    def __init__(self):
        self.cast_cost = 25
        self.active_ability = lambda one, e, f: self.round_attack(e)
        self.passive_ability = lambda: self.the_will_for_life()


class Paladin(Character):

    def heal_all(self, all_friends):
        for friend in all_friends:
            friend.health += self.intelligence + 3 * self.lvl
        heal_for_self = self.intelligence * 10 + 3 * self.lvl
        self.bad_effect_hp = 0
        self.bad_effect_mp = 0
        if self.health + heal_for_self >= self.max_health:
            self.health = self.max_health
        else:
            self.health += heal_for_self
        self.mana -= self.cast_cost

        return self.name + " использует благославление! \n -" + str(self.cast_cost) + " 🔷 " + \
               "+" + str(heal_for_self) + " ♥ " + "\n"

    def gods_bless(self):
        if self.health < self.max_health / 100 * 15:
            self.attack += int(1 + self.attack * 0.06)

    def __init__(self):
        self.gods_bless()
        self.cast_cost = 35
        self.ability_type = 'h'
        self.active_ability = lambda one, e, f: self.heal_all(f)
        self.passive_ability = lambda: self.gods_bless()


class Rubaka(Character):

    def execution(self, enemy):
        calc_reduction = int(enemy.attack / 100 * 15)
        enemy.attack -= calc_reduction
        self.mana -= self.cast_cost

        return self.attack_to(enemy) + self.name + " использует ломкий удар! \n -" + \
               str(calc_reduction) + "🗡 -" + str(self.cast_cost) + "🔷" + "\n"

    def prepare(self):
        if self.start_flag:
            hero_luck = self.luck
            if hero_luck < 1:
                hero_luck = 1
            self.attack += int(1 + self.attack * (random.randint(1, hero_luck) / 100))
            self.start_flag = False

    def __init__(self):
        self.cast_cost = 30
        self.active_ability = lambda one, e, f: self.execution(one)
        self.passive_ability = lambda: self.prepare()


class Graduate(Character):

    def fire(self, all_enemies):
        spell_damage = (self.intelligence + self.lvl) * 4
        for enemy in all_enemies:
            enemy.health -= spell_damage
            enemy.armour //= 2
        self.mana -= self.cast_cost
        self.mana_used = self.cast_cost
        # self.health += 30 +(+ self.multiply_intellect_atk * self.lvl)//2
        return "- Fajro, falo malsupren \n" + self.name + " вызывает огненный шар! \n" + \
               str(spell_damage) + "🗡 -" + str(self.cast_cost) + "🔷" + "\n"

    def mana_sheld(self):
        if self.mana_used > 0:
            self.armour += self.mana_used // 3
            if self.armour > self.max_armour:
                self.armour = self.max_armour
            self.mana_used = 0

    def __init__(self):
        self.cast_cost = 55
        self.active_ability = lambda one, e, f: self.fire(e)
        self.passive_ability = lambda: self.mana_sheld()


class Amateur(Character):

    def fokus(self, all_enemies):
        value = random.randint(0, 100)
        spell_dmg = 0
        spell_heal = 0
        extra_log = ""

        if value < 10 - self.luck:
            spell_heal = -1 * self.intelligence * 3
            extra_log += "Что-то пошло не так. \n" + "Красный огонь обжог " + self.name + ".\n" + \
                         str(spell_heal) + "♥ "
        elif value < 25 - self.luck:
            spell_heal = self.intelligence * 4 + 5
            extra_log += "Зеленный огонёк затянул все раны и царапины. \n" + "+" + str(spell_heal) + "♥ "
        else:
            spell_dmg = value * self.intelligence // 5
            extra_log += "Синее пламя обожгло всех противников \n" + str(spell_dmg) + "🗡"

        for enemy in all_enemies:
            enemy.health -= spell_dmg
        self.health += spell_heal

        self.mana -= self.cast_cost
        return "- Hocus-pocus, ĉarmoj marue ! \n" + self.name + " опять произнёс что-то непонятное и...\n" + \
               extra_log + " -" + str(self.cast_cost) + "🔷" + "\n"

    def mana_regen(self):
        hero_luck = self.luck
        if hero_luck < 0:
            hero_luck = 0
        self.mana += random.randint(hero_luck, hero_luck + 4)

    def __init__(self):
        self.cast_cost = 45
        self.active_ability = lambda one, e, f: self.fokus(e)
        self.passive_ability = lambda: self.mana_regen()


class Warlock(Character):

    def life_drain(self):
        drain_hp = int(self.health / 100 * 40)
        extra_attack = drain_hp // 2
        self.attack += extra_attack
        self.health -= drain_hp
        return "- Mi volas picon, Mephistofeli... \n" + self.name + " взывает к нечистым силам... \n -" + \
               str(drain_hp) + "♥ +" + str(extra_attack) + "🗡" + "\n"

    def cursed_contract(self):
        self.max_health += self.max_mana // 2
        self.health += self.mana // 2
        self.mana = 0
        self.max_mana = 0

    def __init__(self):
        self.cast_cost = 0
        self.cursed_contract()
        self.ability_type = 's'
        self.active_ability = lambda one, e, f: self.life_drain()
        self.passive_ability = lambda: self.cursed_contract()


class Robber(Character):

    def sneak(self, enemy):
        self.crit_rate += 20
        extra_log = self.attack_to(enemy)
        self.crit_rate -= 20
        self.mana -= self.cast_cost
        return self.name + " использует подлый прием! \n" + \
               '-' + str(self.cast_cost) + "🔷" + "\n" + \
               extra_log

    def money_luck(self):
        self.money_bonus = 1.2

    def __init__(self):
        self.cast_cost = 30
        self.money_luck()
        self.active_ability = lambda one, e, f: self.sneak(one)
        self.passive_ability = lambda: 0


class Strelok(Character):

    def combo(self, enemy):
        extra_log = ""
        for n in range(2):
            extra_log += self.attack_to(enemy)
        self.mana -= self.cast_cost
        return self.name + " использует комбинацию атак! \n" + \
               '-' + str(self.cast_cost) + "🔷" + "\n" + \
               extra_log

    def free_wind(self):
        if random.randint(0, 10) < 7 and self.health <= 0:
            self.health = self.health_safe
            self.health_safe = 0

    def __init__(self):
        self.cast_cost = 35
        self.active_ability = lambda one, e, f: self.combo(one)
        self.passive_ability = lambda: self.free_wind()


class Sniper(Character):

    def accurate_shot(self, enemy):
        damage = int(enemy.max_health / 100 * 30)
        enemy.health -= damage
        self.mana -= self.cast_cost
        return self.name + " использует точный выстрел! \n" + \
               "-" + str(damage) + "🗡 " + '-' + str(self.cast_cost) + "🔷" + "\n"

    def night_owl(self):
        hour = time.localtime().tm_hour
        if hour > 21 or hour < 8:
            self.attack = int(self.max_attack * 1.2)

    def __init__(self):
        self.cast_cost = 40
        self.active_ability = lambda one, e, f: self.accurate_shot(one)
        self.passive_ability = lambda: self.night_owl()


def create_class(class_name):
    new_hero = Paladin()
    if class_name == "Странствующий рыцарь":
        new_hero = Knight()
    elif class_name == "Паладин":
        new_hero = Paladin()
    elif class_name == "Рубака":
        new_hero = Rubaka()
    elif class_name == "Выпускник Академии":
        new_hero = Graduate()
    elif class_name == "Чародей-самоучка":
        new_hero = Amateur()
    elif class_name == "Чернокнижник":
        new_hero = Warlock()
    elif class_name == "Разбойник":
        new_hero = Robber()
    elif class_name == "Вольный стрелок":
        new_hero = Strelok()
    elif class_name == "Снайпер":
        new_hero = Sniper()
    return new_hero


def tactic(player, enemy):
    next_act = 'a'
    chance = random.randint(0, 6)
    if player.mana >= player.cast_cost and chance > 1 and \
            player.ability_type == 'd':
        next_act = 'm'
    elif player.health < enemy.health and chance > 4 and \
            player.armour < player.max_armour:
        next_act = 'd'
    elif player.ability_type == 'h' and \
            player.health <= player.max_health // 2 and \
            player.mana >= player.cast_cost:
        next_act = 'm'
    elif player.ability_type == 's' and \
            player.health > player.max_health // 3 * 2 and \
            chance > 0:
        next_act = 'm'

    return next_act
