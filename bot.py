# -*- coding: utf-8 -*-

import asyncio
import logging
import re
from random import randint
from uuid import uuid4

import telepot
import telepot.aio
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineQueryResultArticle, InputTextMessageContent


from config import config


rolls = re.compile(r'((?P<roll_count>\d+)d(?P<dice_type>\d+))((?P<bonus_sign>[+\-])(?P<bonus>\d+))?')

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger(config.BOT_USERNAME)
aio_bot = telepot.aio.Bot(config.BOT_TOKEN)
aio_loop = asyncio.get_event_loop()


async def on_inline_query(msg):
    query_id, from_id, query_string = telepot.glance(msg, flavor='inline_query')

    articles = [
        InlineQueryResultArticle(
            id='internalerror',
            title='Internal Error',
            input_message_content=InputTextMessageContent(
                message_text='Internal Error.'
            )
        )
    ]

    user_roll = None
    user_query = rolls.search(query_string)

    if user_query:
        user_roll = user_query.groupdict()

    logger.info('Inline Query:', query_id, from_id, query_string, 'User roll:', user_roll)

    if user_roll:
        roll_count = int(user_roll['roll_count'])
        dice_type = int(user_roll['dice_type'])
        print(roll_count, dice_type)
        if roll_count not in range(1, 65) or dice_type not in range(4, 101):
            articles = [
                InlineQueryResultArticle(
                    id='wrongnumberortype',
                    title='Wrong number of dices or dice types',
                    input_message_content=InputTextMessageContent(
                        message_text='Number of dices between 1 and 64. Dice type between 4 and 100.'
                    )
                )
            ]
        else:
            if user_roll['bonus_sign'] and user_roll['bonus']:
                roll_count = int(user_roll['roll_count'])
                dice_type = int(user_roll['dice_type'])
                _b = f'{user_roll["bonus_sign"]}{user_roll["bonus"]}'
                user_bonus = int(_b)
                _rolls = []
                result = 0
                if roll_count == 0 or dice_type == 0:
                    articles = [
                        InlineQueryResultArticle(
                            id='wrongquery',
                            title='Wrong Query',
                            input_message_content=InputTextMessageContent(
                                message_text='Wrong Query.'
                            )
                        )
                    ]
                else:
                    for _ in range(roll_count):
                        number = randint(1, dice_type)
                        result += number + user_bonus
                        _rolls.append(f'({number}{_b})')

                    res = f'{query_string}\n{" + ".join(_rolls)} = {result}'

                    articles = [
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=(f'Roll {user_roll["dice_type"]}-sided dice {user_roll["roll_count"]} times. '
                                   f'Bonus {user_roll["bonus_sign"]}{user_roll["bonus"]}'),
                            input_message_content=InputTextMessageContent(
                                message_text=res
                            )
                        )
                    ]
            else:
                roll_count = int(user_roll['roll_count'])
                dice_type = int(user_roll['dice_type'])
                _rolls = []
                result = 0
                if roll_count == 0 or dice_type == 0:
                    articles = [
                        InlineQueryResultArticle(
                            id='wrongquery',
                            title='Wrong Query',
                            input_message_content=InputTextMessageContent(
                                message_text='Wrong Query.'
                            )
                        )
                    ]
                else:
                    for _ in range(roll_count):
                        number = randint(1, dice_type)
                        result += number
                        _rolls.append(f'{number}')

                    res = f'{query_string}\n{" + ".join(_rolls)} = {result}'

                    articles = [
                        InlineQueryResultArticle(
                            id=str(uuid4()),
                            title=f'Roll {user_roll["dice_type"]}-sided dice {user_roll["roll_count"]} times.',
                            input_message_content=InputTextMessageContent(
                                message_text=res
                            )
                        )
                    ]
    else:
        articles = [
            InlineQueryResultArticle(
                id='wrongquery',
                title='Wrong Query',
                input_message_content=InputTextMessageContent(
                    message_text='Wrong Query.'
                )
            )
        ]

    await aio_bot.answerInlineQuery(query_id, articles, cache_time=0)


if __name__ == '__main__':

    aio_loop.create_task(
        MessageLoop(
            aio_bot,
            {
                'inline_query': on_inline_query
            }
        ).run_forever()
    )

    aio_loop.run_forever()
