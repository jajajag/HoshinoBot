import hoshino
import json
import os
import requests
import sqlite3
from datetime import datetime
from bs4 import BeautifulSoup


POOL = ('CN', 'JP', 'TW')
base_url = 'https://wthee.xyz/db/'
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
db_name = 'redive_{}.db'
db_path = os.path.join(os.path.dirname(__file__), db_name)


def update_db(force=False):
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    # Fetch version info
    response = requests.get(base_url)
    # Check if download is successful
    if response.status_code != 200:
        hoshino.logger.warning('Failed to download database version info')
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    # Split text into lines
    lines = soup.find('pre').get_text().splitlines()
    data = {}
    # Go through each line that starts with redive_{pool}.db
    for line in lines:
        for pool in POOL:
            if db_name.format(pool.lower()) == line.split()[0]:
                data[pool] = ' '.join(line.split()[1:3])
    for pool in data:
        # Check if force is True or version is different
        if force or data[pool] != config[pool]['version']:
            response = requests.get(base_url + db_name.format(pool.lower()))
            # Download new database if download is successful
            if response.status_code == 200:
                with open(db_path.format(pool), 'wb') as fp:
                    fp.write(response.content)
                # Update version in config
                config[pool]['version'] = data[pool]
            else:
                hoshino.logger.warning(f'Failed to download {pool} database')
    with open(config_path, 'w') as fp:
        json.dump(config, fp)


def update_config():
    with open(config_path, 'r') as fp:
        config = json.load(fp)
    for pool in POOL:
        # 1. Read all unit data from unit_data table
        conn = sqlite3.connect(db_path.format(pool))
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
            # Handle special case where time is not in datetime format
            start_time = datetime.strptime(start_time, '%Y/%m/%d %H:%M:%S') \
                    if len(start_time) > 10 \
                    else datetime.strptime(start_time, '%Y/%m/%d')
            end_time = datetime.strptime(end_time, '%Y/%m/%d %H:%M:%S') \
                    if len(end_time) > 10 \
                    else datetime.strptime(end_time, '%Y/%m/%d')
            current_time = datetime.now()
            # Find current gacha pool
            if start_time <= current_time <= end_time:
                # Ad unit_id to gacha_bonus_ids if it is up
                if gacha_bonus_id > 0:
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
