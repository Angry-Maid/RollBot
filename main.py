import re
import os
import logging
from random import randint
from json import dumps
from uuid import uuid4

from aiogram import (
    Bot,
    Dispatcher,
    executor
)
from aiogram.types import (
    InlineQuery,
    InputTextMessageContent,
    InlineQueryResultArticle
)
from dotenv import load_dotenv


load_dotenv()


rolls = re.compile(r'((?P<roll_count>\d+)d(?P<dice_type>\d+))((?P<bonus_sign>[+\-])(?P<bonus>\d+))?')

logging.basicConfig(format='%(asctime)s [%(levelname)s]: %(message)s', level=logging.INFO)
logger = logging.getLogger(os.getenv('BOT_USERNAME'))

bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)


internal_error = InlineQueryResultArticle(
    id='internalerror',
    title='Internal Error',
    input_message_content=InputTextMessageContent(
        'Internal error.'
    )
)

wrong_number_or_type = InlineQueryResultArticle(
    id='wrongnumberortype',
    title='Wrong number of dices or dice types',
    input_message_content=InputTextMessageContent(
        'Number of dices between 1 and 64. Dice type between 4 and 100.'
    )
)

wrong_query = InlineQueryResultArticle(
    id='wrongquery',
    title='Wrong Query',
    input_message_content=InputTextMessageContent(
        'Wrong query.'
    )
)


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery):
    (
        query_id,
        from_id,
        query_string
    ) = (
        inline_query.id,
        inline_query.from_user.id,
        inline_query.query or '1d20'
    )

    answer = wrong_query
    input_message = None
    user_roll = None
    title = ''
    _rolls = []
    result = 0
    
    if (user_query := rolls.search(query_string)):
        user_roll = user_query.groupdict()

    logger.info('Inline Query: %s %s %s User roll: %s', query_id, from_id, query_string, dumps(user_roll))

    if user_roll:
        roll_count = int(user_roll['roll_count'])
        dice_type = int(user_roll['dice_type'])

        if roll_count not in range(1, 65) or dice_type not in range(4, 101):
            answer = wrong_number_or_type
        else:
            if user_roll['bonus_sign'] and user_roll['bonus']:
                _b = f"{user_roll['bonus_sign']}{user_roll['bonus']}"
                user_bonus = int(_b)
                for _ in range(roll_count):
                    number = randint(1, dice_type)
                    result += number + user_bonus
                    _rolls.append(f'({number}{_b})')
                
                title = (
                    f'Roll {user_roll["dice_type"]}-sided dice {user_roll["roll_count"]} times. '
                    f'Bonus {user_roll["bonus_sign"]}{user_roll["bonus"]}'
                )
                input_message = InputTextMessageContent(
                    f'{query_string}\n{" + ".join(_rolls)} = {result}'
                )
            else:
                for _ in range(roll_count):
                    number = randint(1, dice_type)
                    result += number
                    _rolls.append(str(number))
                
                title = f'Roll {user_roll["dice_type"]}-sided dice {user_roll["roll_count"]} times.'
                input_message = InputTextMessageContent(
                    f'{query_string}\n{" + ".join(_rolls)} = {result}'
                )

    if input_message:
        answer = InlineQueryResultArticle(
            id=str(uuid4()),
            title=title,
            input_message_content=input_message
        )

    await bot.answer_inline_query(
        inline_query.id,
        results=[answer],
        cache_time=0
    )


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
