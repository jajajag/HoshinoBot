import asyncio
import re
from aiocqhttp.message import escape
from hoshino import config, Service
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter
from openai import OpenAI


sv_help = '''
调用大模型回答问题
[那我问你：XXX] 问大模型问题
'''
sv = Service('llm', help_=sv_help, bundle='llm',
             enable_on_default=True)


# Maximum number of questions that can be asked per day
_max_daily = 10
llm_limiter = DailyNumberLimiter(_max_daily)
max_output_tokens = 10000


# Initialize the openai client
client = OpenAI(api_key=config.priconne.llm.API_KEY)
                #base_url="https://api.deepseek.com")


@sv.on_rex(r'^那我[问問]你[：:]')
async def llm(bot, ev: CQEvent):
    # User info
    user_id = ev.user_id
    content = ev.message.extract_plain_text()[5:]

    # Skip if the message is empty
    if re.fullmatch(r'^[^A-Za-z\u4e00-\u9fff]*$', content):
        return

    # Check if the user has reached the limit
    if not user_id in config.SUPERUSERS and not llm_limiter.check(user_id):
        await bot.finish(ev, f'已达到每日提问次数上限（{_max_daily}）！',
                       at_sender=True)
    llm_limiter.increase(user_id)

    try:
        response = await asyncio.to_thread(
            client.responses.create,
            model='gpt-5-mini',
            tools=[{
                'type': 'web_search',
                'search_context_size': 'low',
            }],
            input=content,
            max_output_tokens=max_output_tokens,
        )
    except:
        # Insufficient balance
        await bot.finish(ev, '没钳了没钳了！', at_sender=True)

    # Get the response
    await bot.send(ev, escape(response.output_text))
