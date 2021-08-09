import pymysql.cursors


def get_connect1():
    connection = pymysql.connect(
        host='eu-cdbr-west-01.cleardb.com',
        user='bd44ae7cb085a1',
        password='04bfb52d',
        db='heroku_86f6421dc33a932',
        cursorclass=pymysql.cursors.DictCursor,
        port=3306
    )

    return connection


def get_connect():
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        db='vk_bot',
        cursorclass=pymysql.cursors.DictCursor,
        port=3307
    )

    return connection

