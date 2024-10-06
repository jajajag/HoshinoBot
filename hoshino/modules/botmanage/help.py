from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('_help_', manage_priv=priv.SUPERUSER, visible=False)

TOP_MANUAL = '''
以下是nnk目前的功能
【简单指令】
(国|台|日)作业: 会战作业
(国|台|日)rank: rank表
(国|台|日)服日程: 日程
(国|台|日)服新闻: 新闻
(国|台)千里眼: 千里眼
怎么拆: JJC阵容查询
今日老婆: 今天的群老婆
抽签: 如抽签，抽中二签
选图(列表|XX): 表情模板
XX.jpg: 生成XX的表情
nnk(来一井|十连|单抽)
官漫XXX: 第XXX话官漫
大家说X回答X:  你问我答
(涩图|来一张XX涩图)
(转秒XX|合刀XX XX XX)
【查详细用法】
竞技场帮助:台二JJC提醒
马娘帮助: 赛马娘相关
会战排名帮助: 会战排名
帮助头像表情包: 表情包
帮助抽老婆: 抽(牛)老婆
帮助pjsk贴纸: pjsk表情
【管理】
lssv: 查看模块的开关状态
(启|禁)用XX: 开关模块
※Hoshino开源Project: 
github.com/Ice9Coffee/HoshinoBot
'''.strip()
# 魔改请保留 github.com/Ice9Coffee/HoshinoBot 项目地址


def gen_service_manual(service:  Service, gid:  int): 
    spit_line = '=' * max(0, 18 - len(service.name))
    manual = [f"|{'○' if service.check_enabled(gid) else '×'}| {service.name} {spit_line}"]
    if service.help: 
        manual.append(service.help)
    return '\n'.join(manual)


def gen_bundle_manual(bundle_name, service_list, gid): 
    manual = [bundle_name]
    service_list = sorted(service_list, key=lambda s:  s.name)
    for s in service_list: 
        if s.visible: 
            manual.append(gen_service_manual(s, gid))
    return '\n'.join(manual)


@sv.on_prefix('help', '帮助')
@sv.on_suffix('help', '帮助')
async def send_help(bot, ev:  CQEvent): 
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
    # else:  ignore
