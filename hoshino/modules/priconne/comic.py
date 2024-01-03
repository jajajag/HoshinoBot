import os
import re
import random
import asyncio
from bilibili_api import user
from urllib.parse import urljoin, urlparse, parse_qs
try:
    import ujson as json
except:
    import json

from hoshino import aiorequests, R, Service
from hoshino.typing import *

sv_help = '''
官方四格漫画更新
[官漫132] 阅览指定话
'''.strip()
sv = Service('pcr-comic', help_=sv_help, bundle='pcr订阅', 
             enable_on_default=False)

def load_index():
    with open(R.get('img/priconne/comic/index.json').path, 
              encoding='utf8') as f:
        return json.load(f)

def get_pic_name(id_):
    pre = 'episode_'
    end = '.jpg'
    return f'{pre}{id_}{end}'


@sv.on_prefix('官漫')
async def comic(bot, ev: CQEvent):
    episode = ev.message.extract_plain_text()
    if not re.fullmatch(r'\d{0,3}', episode):
        return
    episode = episode.lstrip('0')
    if not episode:
        await bot.send(ev, '请输入漫画集数 如：官漫132', at_sender=True)
        return
    index = load_index()
    if episode not in index:
        await bot.send(ev, f'未查找到第{episode}话，敬请期待官方更新', 
                       at_sender=True)
        return
    pic = R.img('priconne/comic/', get_pic_name(episode)).cqcode
    msg = f'\n第{episode}话\n{pic}'
    await bot.send(ev, msg, at_sender=True)


async def download_img(save_path, link):
    '''
    从link下载图片保存至save_path（目录+文件名）
    会覆盖原有文件，需保证目录存在
    '''
    sv.logger.info(f'download_img from {link}')
    resp = await aiorequests.get(link, stream=True)
    sv.logger.info(f'status_code={resp.status_code}')
    if 200 == resp.status_code:
        if re.search(r'image', resp.headers['content-type'], re.I):
            sv.logger.info(f'is image, saving to {save_path}')
            with open(save_path, 'wb') as f:
                f.write(await resp.content)
                sv.logger.info('saved!')


async def download_comic(id_):
    '''
    下载指定id的官方四格漫画，同时更新漫画目录index.json
    episode_num可能会小于id
    '''
    base = 'https://comic.priconne-redive.jp/api/detail/'
    save_dir = R.img('priconne/comic/').path
    index = load_index()

    # 先从api获取detail，其中包含图片真正的链接
    sv.logger.info(f'getting comic {id_} ...')
    url = base + id_
    sv.logger.info(f'url={url}')
    resp = await aiorequests.get(url)
    sv.logger.info(f'status_code={resp.status_code}')
    if 200 != resp.status_code:
        return
    data = await resp.json()
    data = data[0]

    episode = data['episode_num']
    title = data['title']
    link = data['cartoon']
    index[episode] = {'title': title, 'link': link}
    sv.logger.info(f'episode={index[episode]}')

    # 下载图片并保存
    await download_img(os.path.join(save_dir, get_pic_name(episode)), link)

    # 保存官漫目录信息
    with open(os.path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False)


@sv.scheduled_job('cron', minute='*/5', second='25')
async def update_seeker():
    '''
    轮询官方四格漫画更新
    若有更新则推送至订阅群
    '''
    index = load_index()

    # 获取最新漫画信息
    # From 是年年嗷嗷嗷(https://space.bilibili.com/3260075/dynamic)
    u = user.User(3260075)
    res = await u.get_dynamics()
    link = None
    # Check the newest few dynamics
    for card in res['cards']:
        # Continue if no item/description/pictures in the dynamic
        if 'item' not in card['card']: continue
        item = card['card']['item']
        if 'description' not in item or 'pictures' not in item: continue
        if '四格漫画更新' not in item['description']: continue
        rex = re.search(r'第\d+话', item['description'])
        if rex is None: continue
        # The newest comic dynamic found
        episode = rex.group(0)[1:-1]
        for picture in item['pictures']:
            if picture['img_height'] > 512 and picture['img_width'] > 512:
                link = picture['img_src']
                break
        if link is not None: break
    # Return if no comic found in the dynamics
    else: return

    # 检查是否已在目录中
    # 同一episode可能会被更新为另一张图片（官方修正），此时episode不变而id改变
    # 所以需要两步判断
    if episode in index:
        old_link = index[episode]
        # Check if link has changed
        if link == old_link:
            sv.logger.info('未检测到官漫更新')
            return

    # 确定已有更新，下载图片
    sv.logger.info(f'发现更新 episode={episode}')
    save_dir = R.img('priconne/comic/').path
    await download_img(os.path.join(save_dir, get_pic_name(episode)), link)

    # 保存官漫目录信息
    index[episode] = link
    with open(os.path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False)

    # 推送至各个订阅群
    pic = R.img('priconne/comic', get_pic_name(episode)).cqcode
    msg = f'第{episode}话\n{pic}'
    await sv.broadcast(msg, 'PCR官方四格', 0.5)
