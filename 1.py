# -*- coding: utf-8 -*-
import json
import time
import random
import sqlite3
import requests
import datetime

# 打包 venv\Scripts\pyinstaller.exe -F 1.py

uid = 0
loop_time = 60
last_fans = 0
last_guard = 0


# 字符串是否是数字
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


while True:
    uid = input("请输入监测用户UID：")
    if not is_number(uid):
        print("请输入正确的UID")
        continue
    loop_time = input("请输入监测周期（秒）：")
    if not is_number(loop_time):
        print("请输入数字")
        continue
    else:
        print("开始运行...")
        break

headers1 = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'text/plain;charset=UTF-8',
    # 'Referer': referer,
    'origin': 'https://live.bilibili.com',
    # 'cookie': 'l=v',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3875.400 QQBrowser/10.8.4492.400'
}


# 配置数据库
def config_db():
    global con, cur
    con = sqlite3.connect("user_data.db")
    cur = con.cursor()
    # 创建表user
    sql = "CREATE TABLE IF NOT EXISTS user(mid TEXT,name TEXT,fans TEXT,guard TEXT,data TEXT)"
    cur.execute(sql)


def get_base_info(uid):
    API_URL = 'https://account.bilibili.com/api/member/getCardByMid?mid=' + uid
    ret = requests.get(API_URL)
    ret = ret.json()
    # nonebot.logger.info(ret)
    return ret


def get_room_id(uid):
    API_URL = 'https://api.live.bilibili.com/room/v2/Room/room_id_by_uid?uid=' + uid
    ret = requests.get(API_URL)
    ret = ret.json()
    room_id = ret['data']['room_id']
    return room_id


def get_guard_info(uid, room_id):
    API_URL = 'https://api.live.bilibili.com/xlive/app-room/v2/guardTab/topList?roomid=' + str(
        room_id) + '&page=1&ruid=' + uid + '&page_size=0'
    ret = requests.get(API_URL)
    ret = ret.json()
    return ret


def get_now_time():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def run():
    global last_fans
    global last_guard
    base_info_json = get_base_info(uid)
    room_id = get_room_id(uid)
    guard_info_json = get_guard_info(uid, room_id)
    now_time = get_now_time()
    # 数据插入数据库
    sql = "insert into user(mid, name, fans, guard, data) values (?, ?, ?, ?, ?)"
    cur.execute(sql, (base_info_json['card']['mid'], base_info_json['card']['name'], base_info_json['card']['fans'],
                      guard_info_json['data']['info']['num'], now_time))
    con.commit()

    msg = now_time + ' | 用户名：' + base_info_json['card']['name'] + ' | UID：' + str(base_info_json['card']['mid']) + \
          ' | 房间号：' + str(room_id) + ' | 粉丝增加：' + str(base_info_json['card']['fans'] - last_fans) + ' | 粉丝数：' + \
          str(base_info_json['card']['fans']) + ' | 舰团增加：' + str(guard_info_json['data']['info']['num'] - last_guard) + \
          ' | 舰团数：' + str(guard_info_json['data']['info']['num'])

    print(msg)

    last_fans = base_info_json['card']['fans']
    last_guard = guard_info_json['data']['info']['num']



# 创建数据库
print("创建数据库...")
config_db()
# 首次运行
base_info_json = get_base_info(uid)
room_id = get_room_id(uid)
guard_info_json = get_guard_info(uid, room_id)
last_fans = base_info_json['card']['fans']
last_guard = guard_info_json['data']['info']['num']
now_time = get_now_time()
msg = now_time + ' | 用户名：' + base_info_json['card']['name'] + ' | UID：' + str(base_info_json['card']['mid']) + \
      ' | 房间号：' + str(room_id) + ' | 粉丝增加：0' + ' | 粉丝数：' + str(base_info_json['card']['fans']) + \
      ' | 舰团增加：0' + ' | 舰团数：' + str(guard_info_json['data']['info']['num'])
print(msg)
# 数据插入数据库
sql = "insert into user(mid, name, fans, guard, data) values (?, ?, ?, ?, ?)"
cur.execute(sql, (base_info_json['card']['mid'], base_info_json['card']['name'], base_info_json['card']['fans'],
                  guard_info_json['data']['info']['num'], now_time))
con.commit()


while True:
    time.sleep(int(loop_time))
    run()
