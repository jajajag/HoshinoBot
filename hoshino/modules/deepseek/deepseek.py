from hoshino import config, Service
from hoshino.typing import *
from hoshino.util import DailyNumberLimiter


sv_help = '''
调用deepseek回答问题
[那我问你XXX] 问deepseek问题
'''
sv = Service('deepseek', help_=sv_help, bundle='deepseek', 
             enable_on_default=True)


# Maximum number of questions that can be asked per day
_max_daily = 5
deepseek_limiter = DailyNumberLimiter(2)
max_output_tokens = 100


# Initialize the deepseek client
client = OpenAI(api_key=config.priconne.deepseek.api_key,
                base_url="https://api.deepseek.com")


@sv.on_prefix('那我问你', '那我問你')
async def deepseek(bot, ev: CQEvent):
    # User info
    user_id = ev.user_id
    cmd = ev.message.extract_plain_text()
    content = cmd[4:]

    # Check if the user has reached the limit
    if not user_id and not deepseek_limiter.check(user_id):
        await bot.send(ev, f'已达到每日提问次数上限（{_max_daily}）！',
                       at_sender=True)
    deepseek_limiter.increase(user_id)

    try:
        response = client.chat.completions.create(
            # Target model (deepseek-chat or deepseek-reasoner)
            model="deepseek-chat",
            messages=[{"role": "user", "content": content}],
            # Control the temperature of the response (0 to 1, default 0.7)
            #temperature=0.7,
            max_tokens=max_output_tokens,
            stream=False
        )
    except:
        # Insufficient balance
        await bot.finish(ev, '没钳了没钳了！', at_sender=True)

    # Get the response
    await bot.send(ev, response.choices[0].message['content'])
