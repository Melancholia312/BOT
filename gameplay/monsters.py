import time
import random

random.seed()


class Monster:
    lvl = 1  # random numbers for test
    health = 80
    max_health = 80
    armour = 2
    max_armour = 2
    attack = 30
    tier = 1
    luck = 5
    name = "karp pererostok"
    good_effect_hp = 1
    bad_effect_hp = 0
    reward = 10

    def __init__(self):
        pass

    def get_state(self, inf):
        self.health = inf["HP"]
        self.max_health = self.health
        self.luck = inf["luck"]
        self.name = inf["name"]
        self.armour = inf["armor"]
        self.attack = inf["ATK"]
        self.tier = inf["tier"]
        self.reward = inf["reward_money"]
        self.lvl = self.tier
        self.max_armour = self.armour

    def diversity(self):
        self.health += random.randint(-2, 2) * self.tier
        self.attack += random.randint(-1, 1) * self.tier

    def attack_to(self, enemy):
        atc_log = ""  # self.name + " атакует " + enemy.name + "." + "\n"
        chance = random.randint(1, 100)
        calc_damage = self.attack 
        attack_des = [" укусил ", " поцарапал ", " ударил "]

        if chance <= self.luck:
            crit_bonus = chance / 10 + 1
            
            if crit_bonus > 1.5:
                crit_bonus = 1.5
                
            calc_damage = int(calc_damage * crit_bonus)
            atc_log += self.name + " наносит критический урон! " + "-" + str(calc_damage) + "\n"

        elif chance < 75 + self.luck:
            base_bonus = chance / 100 + 0.2
            
            if base_bonus > 1:
                base_bonus = 1
                
            calc_damage = int(calc_damage * base_bonus)
            atc_log += self.name + attack_des[random.randint(0, len(attack_des) - 1)] + enemy.name + ". " + \
                       "-" + str(calc_damage) + "\n"

            if chance % 17 == 0:
                calc_bad_effect = int(enemy.health / 100 * 5) + 5
                atc_log += "Кровотечение у " + enemy.name + '.' + "\n" + \
                           '-' + str(calc_bad_effect) + " hp/sec" + "\n"
                enemy.bad_effect_hp += calc_bad_effect
        else:
            calc_damage = 0
            atc_log += self.name + " промахнулся" + "." + "\n"

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
        extra_armour = random.randint(self.luck, self.luck + 5) // 2 + self.lvl * 2
        self.armour += extra_armour
        def_log = ""
        if self.armour > self.max_armour:
            self.armour = self.max_armour
            def_log = self.name + " затаился. " + "броня " + str(self.armour) + "\n"
        else:
            def_log = self.name + " затаился. " + "+броня " + str(extra_armour) + "\n"
        return def_log

    def post_fight(self):
        if self.health + self.good_effect_hp <= self.max_health:
            self.health += self.good_effect_hp

        self.health -= self.bad_effect_hp


def generate_contract(hero_lvl, monster_inf, group=True):
    new_contract = []

    if not group:
        new_monster = Monster()
        new_monster.get_state(monster_inf)
        new_monster.diversity()

        return [new_monster]
    steck_size = 1
    monster_lvl = hero_lvl - monster_inf["tier"]
    if monster_lvl > 13:
        steck_size = 5
    elif monster_lvl > 8:
        steck_size = 3 + random.randint(0, 1)
    elif monster_lvl > 3:
        steck_size = 2

    for i in range(steck_size):
        new_monster = Monster()
        new_monster.get_state(monster_inf)
        new_monster.diversity()

        new_contract.append(new_monster)

    return new_contract
