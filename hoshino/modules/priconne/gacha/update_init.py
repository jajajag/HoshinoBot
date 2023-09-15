import json
import os
import requests
import sqlite3
from datetime import datetime

POOL = ('CN', 'JP', 'TW')
base_url = 'https://raw.githubusercontent.com/Expugn/priconne-database/master/'
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
db_path = os.path.join(os.path.dirname(__file__), 'master_{}.db')

def check_version():
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    # Download version.json
    response = requests.get(base_url + 'version.json')
    data = response.json()
    # Check if download is successful
    if response.status_code != 200:
        return
    for pool in POOL:
        # Check version, download new database if new db is available
        if data[pool]['version'] != config[pool]['version']:
            config[pool]['version'] = data[pool]['version']
            response = requests.get(base_url + db_name)
            # Download new database if download is successful
            if response.status_code == 200:
                with open(db_path.format(pool.lower()), 'wb') as fp:
                    fp.write(response.content)
            # Update version in config
            config[pool]['version'] = data[pool]['version']
    with open(config_path, 'w') as fp:
        json.dump(config, fp)

def update_pool_fromdb():
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    for pool in POOL:
        # 1. Read all unit data from unit_data table
        conn = sqlite3.connect(db_path.format(pool.lower()))
        cursor = conn.cursor()
        cursor.execute(('SELECT cutin_1, rarity, is_limited, move_speed'
                        ' FROM unit_data'))
        rows = cursor.fetchall()
        # 1.1 Read unit_id from unit_data table
        config[pool]['star1'], config[pool]['star2'] = [], []
        config[pool]['star3'] = []
        for row in rows:
            unit_id, rarity, is_limited, move_speed = row
            unit_id = int(unit_id / 100)
            # Break if unit_id is over 1900
            if unit_id > 1900:
                break
            if is_limited or move_speed == 0:
                continue
            elif rarity == 1:
                config[pool]['star1'].append(unit_id)
            elif rarity == 2:
                config[pool]['star2'].append(unit_id)
            else: # Otherwise the rarity should be 3
                config[pool]['star3'].append(unit_id)
        # 2. Read pickup chara data from gacha_exchange_lineup table
        cursor.execute(('SELECT start_time, end_time, unit_id,'
                        'gacha_bonus_id FROM gacha_exchange_lineup'))
        rows = cursor.fetchall()
        # 2.1 Find current pickup chara using current datetime
        unit_ids, gacha_bonus_ids = [], []
        for row in rows:
            start_time, end_time, unit_id, gacha_bonus_id = row
            unit_id = int(unit_id / 100)
            start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S')
            end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S')
            current_time = datetime.now()
            # Find current gacha pool
            if start_time <= current_time <= end_time:
                # Ad unit_id to gacha_bonus_ids if it is up
                if gacha_bonus_id < 0:
                    gacha_bonus_ids.append(unit_id)
                else:
                    unit_ids.append(unit_id)
        # Use tenjo chara if ther is no pickup chara
        if len(gacha_bonus_ids) == 0:
            unit_ids, gacha_bonus_ids = [], unit_ids
        # Here we suppose that there are only star 3 pickup chara
        for unit_id in unit_ids:
            if unit_id not in config[pool]['star3']:
                config[pool]['star3'].append(unit_id)
        config[pool]['up'] = gacha_bonus_ids
        cursor.close()
        conn.close()
    with open(config_path, 'w') as fp:
        json.dump(config, fp)

async def update():
    check_version()
    update_pool_fromdb()
