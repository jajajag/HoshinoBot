from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = '''
以下是目前nnk的功能（有些需要@nnk或叫nnk）
【会战类】
作业：查看会战作业网
(A|B|C)作业：各阶段作业表
会战排行XX：XX公会排行
公会排行：本公会排行
【功能类】
(国|b|台|日)rank：rank表
(国|台|日)服日(程|历)：日程
(国|台)服新闻：X服新闻
刷图：查看刷图推荐
(国|台)服千里眼：千里眼
怎么拆布丁望裁缝黄骑老师：JJC阵容查询
(竞技场|详细)查询 ID：查看台二JJC
【抽签类】
@nnk (来一井|十连|单抽)
@nnk (抽签|运势)：抽运势
@nnk 抽XX签：如抽中二签
.r：扔骰子1-100
【语音类】
@nnk 骂我：xcw骂我
搜无损 歌曲名：搜无损歌曲
【图片类】
(涩图|来一张涩图|不够涩)
选图列表：查看表情模板
选图[栞栞]：选表情模板
XX.jpg：生成XX的表情
【其他】
[帮助pcr会战]
[lssv] 查看模块的开关状态
[启/禁用+空格+service]
※Hoshino开源Project：
github.com/Ice-Cirno/HoshinoBot
'''.strip()
# 魔改请保留 github.com/Ice-Cirno/HoshinoBot 项目地址


def gen_service_manual(service: Service, gid: int):
    spit_line = '=' * max(0, 18 - len(service.name))
    manual = [f"|{'○' if service.check_enabled(gid) else '×'}| {service.name} {spit_line}"]
    if service.help:
        manual.append(service.help)
    return '\n'.join(manual)


def gen_bundle_manual(bundle_name, service_list, gid):
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s: s.name)
    for s in service_list:
        if s.visible:
            manual.append(gen_service_manual(s, gid))
    return '\n'.join(manual)


@sv.on_prefix('help', '帮助')
async def send_help(bot, ev: CQEvent):
    gid = ev.group_id
    arg = ev.message.extract_plain_text().strip()
    bundles = Service.get_bundles()
    services = Service.get_loaded_services()
    if not arg:
        await bot.send(ev, TOP_MANUAL)
    elif arg in bundles:
        msg = gen_bundle_manual(arg, bundles[arg], gid)
        await bot.send(ev, msg)
    elif arg in services:
        s = services[arg]
        msg = gen_service_manual(s, gid)
        await bot.send(ev, msg)
    # else: ignore
