import asyncio
import httpx
import os
import itertools
from bilibili_api import article, user, Credential
from datetime import datetime
from hoshino import config, util, R
from hoshino.typing import CQEvent
from . import sv


@sv.on_rex(r'^(\*?([日台国陆b])服?([前中后]*)卫?)?rank(表|推荐|指南)?$')
async def rank_sheet(bot, ev):
    match = ev['match']
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev, '\n请问您要查询哪个服务器的rank表？'\
                '\n(日|台|国|陆|b)rank表', at_sender=True)
        return
    if is_jp:
        await bot.send(ev, f"\n休闲：拉满\n一档：问你家会长", at_sender=True)
    elif is_tw:
        await bot.send(ev, f"\n休闲：拉满\n一档：问你家会长", at_sender=True)
    elif is_cn:
        await bot.send(
                ev, f"\nhttps://docs.qq.com/sheet/DYWxDbGdRYWV1bHFv?tab=jdyikm",
                at_sender=True)


@sv.on_rex(r'^(\*?([日台国陆b])服?)?作业$')
async def rank_sheet(bot, ev):
    match = ev['match']
    is_jp = match.group(2) == '日'
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_jp and not is_tw and not is_cn:
        await bot.send(ev, '\n请问您要查询哪个服务器的作业？'\
                '\n(日|台|国|陆|b)作业', at_sender=True)
        return
    if is_jp:
        await bot.send(ev, f"\nhttps://www.aikurumi.cn/gvg;serverType=jp",
                       at_sender=True)
    elif is_tw:
        await bot.send(ev, f"\nhttps://www.aikurumi.cn/gvg;serverType=tw",
                       at_sender=True)
    elif is_cn:
        await bot.send(ev, f"\nhttps://www.caimogu.cc/gzlj", at_sender=True)


@sv.on_fullmatch('刷图')
async def farm_sheet(bot, ev):
    await bot.send(
            ev, f"\nhttps://docs.qq.com/sheet/DYWxDbGdRYWV1bHFv?tab=r0h0ei",
            at_sender=True)


@sv.on_fullmatch('jjc', 'JJC', 'JJC作业', 'JJC作业网', 'JJC数据库', 'jjc作业', 'jjc作业网', 'jjc数据库')
async def say_arina_database(bot, ev):
    await bot.send(ev, '公主连接Re:Dive 竞技场编成数据库\n日文：https://nomae.net/arenadb \n中文：https://pcrdfans.com/battle')


OTHER_KEYWORDS = '【日rank】【台rank】【b服rank】【jjc作业网】【黄骑充电表】【一个顶俩】'
PCR_SITES = f'''
【繁中wiki/兰德索尔图书馆】pcredivewiki.tw
【日文wiki/GameWith】gamewith.jp/pricone-re
【日文wiki/AppMedia】appmedia.jp/priconne-redive
【竞技场作业库(中文)】pcrdfans.com/battle
【竞技场作业库(日文)】nomae.net/arenadb
【论坛/NGA社区】nga.178.com/thread.php?fid=-10308342
【iOS实用工具/初音笔记】nga.178.com/read.php?tid=14878762
【安卓实用工具/静流笔记】nga.178.com/read.php?tid=20499613
【台服卡池千里眼】nga.178.com/read.php?tid=28236922
【日官网】priconne-redive.jp
【台官网】www.princessconnect.so-net.tw

===其他查询关键词===
{OTHER_KEYWORDS}
※B服速查请输入【bcr速查】'''

BCR_SITES = f'''
【妈宝骑士攻略(懒人攻略合集)】nga.178.com/read.php?tid=20980776
【机制详解】nga.178.com/read.php?tid=19104807
【初始推荐】nga.178.com/read.php?tid=20789582
【术语黑话】nga.178.com/read.php?tid=18422680
【角色点评】nga.178.com/read.php?tid=20804052
【秘石规划】nga.178.com/read.php?tid=20101864
【卡池亿里眼】nga.178.com/read.php?tid=20816796
【为何卡R卡星】nga.178.com/read.php?tid=20732035
【推图阵容推荐】nga.178.com/read.php?tid=21010038

===其他查询关键词===
{OTHER_KEYWORDS}
※日台服速查请输入【pcr速查】'''

@sv.on_fullmatch('pcr速查', 'pcr图书馆', '图书馆')
async def pcr_sites(bot, ev: CQEvent):
    await bot.send(ev, PCR_SITES, at_sender=True)
    await util.silence(ev, 60)
@sv.on_fullmatch('bcr速查', 'bcr攻略')
async def bcr_sites(bot, ev: CQEvent):
    await bot.send(ev, BCR_SITES, at_sender=True)
    await util.silence(ev, 60)


YUKARI_SHEET_ALIAS = map(lambda x: ''.join(x), itertools.product(('黄骑', '酒鬼'), ('充电', '充电表', '充能', '充能表')))
YUKARI_SHEET = f'''
{R.img('priconne/quick/黄骑充电.png').cqcode}'''
@sv.on_fullmatch(YUKARI_SHEET_ALIAS)
async def yukari_sheet(bot, ev):
    await bot.send(ev, YUKARI_SHEET, at_sender=True)
    await util.silence(ev, 60)


DRAGON_TOOL = f'''
拼音对照表：{R.img('priconne/KyaruMiniGame/注音文字.jpg').cqcode}{R.img('priconne/KyaruMiniGame/接龙.jpg').cqcode}
龍的探索者們小遊戲單字表 https://hanshino.nctu.me/online/KyaruMiniGame
镜像 https://hoshino.monster/KyaruMiniGame
网站内有全词条和搜索，或需科学上网'''
@sv.on_fullmatch('一个顶俩', '拼音接龙', '韵母接龙')
async def dragon(bot, ev):
    await bot.send(ev, DRAGON_TOOL, at_sender=True)
    await util.silence(ev, 60)


# Borrowed from https://github.com/azmiao/uma_plugin
async def download_image(img_path, url):
    response = httpx.get(url, timeout=10)
    with open(img_path, 'wb') as f:
        f.write(response.read())


async def send_image(url):
    file_name = url.split('/')[-1]
    img_path = os.path.join(R.img('priconne').path, f'quick/{file_name}')
    if not os.path.exists(img_path):
        await download_image(img_path, url)
    return R.img(f'priconne/quick/{file_name}').cqcode


async def send_image_tw(urls, height_limit):
    found = False
    for url in urls:
        file_name = url.split('/')[-1]
        img_path = os.path.join(R.img('priconne').path, f'quick/{file_name}')
        if not os.path.exists(img_path):
            await download_image(img_path, url)
        # JAG: Check image height to decide the real future gacha
        img = R.img(f'priconne/quick/{file_name}').open()
        width, height = img.size
        # Return the 千里眼 and 专二表
        if found:
            return first_cqcode + R.img(f'priconne/quick/{file_name}').cqcode
        elif height > height_limit:
            found = True
            first_cqcode = R.img(f'priconne/quick/{file_name}').cqcode 


@sv.on_rex(r'^(\*?([台国陆b])服?)?千里眼$')
async def future_gacha(bot, ev):
    match = ev['match']
    is_tw = match.group(2) == '台'
    is_cn = match.group(2) and match.group(2) in '国陆b'
    if not is_tw and not is_cn:
        await bot.send(ev, '\n请问您要查询哪个服务器的千里眼？'\
                '\n(台|国|陆|b)千里眼', at_sender=True)
        return

    # 源自UP主镜华妈妈我要喝捏捏：https://space.bilibili.com/1343686（已弃坑）
    # 源自UP主Kumiko_kawaii：https://space.bilibili.com/511146986
    if is_tw:
        # JAG: Cookies are manually obtained from the browser
        # https://nemo2011.github.io/bilibili-api/#/get-credential
        credential = Credential(**config.priconne.bili_cookies)
        u = user.User(511146986, credential=credential)
        articles = await u.get_articles()
        # Find article titled '千里眼' from most recent to oldest
        for ar in articles['articles']:
            if '千里眼' in ar['title']: break
        else: return
        # Fetch article content
        ar = article.Article(ar['id'])
        await ar.fetch_content()
        urls = [node['url'] for node in ar.json()['children'] if node['type'] == 'ImageNode']
        await bot.send(ev, await send_image_tw(urls, 3200), at_sender=True)
    # 源自UP主Columba-丘比：https://space.bilibili.com/25586360
    elif is_cn:
        ar = article.Article(15264705)
        await ar.fetch_content()
        # Find first image node
        for node in ar.json()['children']:
            if node['type'] == 'ImageNode': break
        else: return
        url = node['url']
        await bot.send(ev, await send_image(url), at_sender=True)
