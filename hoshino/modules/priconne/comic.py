import os
import re
import random
import asyncio
from bilibili_api import user, Credential
from hoshino import config
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
#@sv.scheduled_job('cron', hour='*/6')
async def update_seeker():
    '''
    轮询官方四格漫画更新
    若有更新则推送至订阅群
    '''
    # 检查是否已在目录中
    index = load_index()

    # JAG: Cookies are manually obtained from the browser
    # https://nemo2011.github.io/bilibili-api/#/get-credential
    credential = Credential(**config.priconne.bili_cookies)

    # JAG: Fetch the comic from the user's dynamics
    # From 是年年嗷嗷嗷(https://space.bilibili.com/3260075/dynamic)
    u = user.User(3260075, credential=credential)
    res = await u.get_dynamics_new()
    index_new = {}
    # Check the newest few dynamics
    for item in res['items']:
        # Continue if the dynamic is not an opus
        if item['modules']['module_dynamic']['major'] is None \
                or 'opus' not in item['modules']['module_dynamic']['major']:
            continue
        opus = item['modules']['module_dynamic']['major']['opus']
        # Continue if the dynamic is not a comic update
        if '四格漫画更新' not in opus['summary']['text']: continue
        matches = re.findall(r'第\d+话', opus['summary']['text'])
        for i in range(len(matches)):
            index_new[matches[i][1:-1]] = opus['pics'][i]['url']

    # Find new updates, return if no updates
    index_new = {k: v for k, v in index_new.items() if k not in index}
    if index_new == {}: return

    # 确定已有更新，下载图片
    save_dir = R.img('priconne/comic/').path
    for episode, link in index_new.items():
        sv.logger.info(f'发现更新 episode={episode}')
        await download_img(os.path.join(save_dir, get_pic_name(episode)), link)
        index[episode] = link

    # 保存官漫目录信息
    with open(os.path.join(save_dir, 'index.json'), 'w', encoding='utf8') as f:
        json.dump(index, f, ensure_ascii=False)

    # 推送至各个订阅群
    pic = R.img('priconne/comic', get_pic_name(episode)).cqcode
    msg = f'第{episode}话\n{pic}'
    await sv.broadcast(msg, 'PCR官方四格', 0.5)
