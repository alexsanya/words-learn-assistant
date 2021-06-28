import logging
from typing import Callable
import aiogram.utils.markdown as md
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State
from aiogram import Bot, Dispatcher, executor, types
from middlewares import AccessMiddleware
from vocabulary import Record, Word, vocabulary, MEMORIZATION_TRESHOLD
from config import TELEGRAM_API_TOKEN, TELEGRAM_ACCESS_ID

logging.basicConfig(level=logging.INFO)

words_list = State()

bot = Bot(token=TELEGRAM_API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(AccessMiddleware(TELEGRAM_ACCESS_ID))

class InvalidDataError(Exception):
    pass

def format_list(list: list[Record], render: Callable[[Record], str]) -> str:
    lines = [f"{num}. {render(item)}" for num, item in enumerate(list, start=1)]
    return md.text(*lines, sep='\n')

async def getIndexesFromMsg(message: types.Message, max_number: int) -> list[int]:
    try:
        args = message.get_args()
        parsed_indexes = [int(wid) for wid in args.split()]
        if (max(parsed_indexes) > max_number) | (min(parsed_indexes) < 1):
            await message.reply(f"Indexes should be numbers from 1 to {max_number}")
            raise InvalidDataError from None
        return parsed_indexes
    except ValueError:
        await message.reply("Indexes should be numbers")
        raise InvalidDataError from None

@dp.message_handler(commands=['add'])
async def add_new_word(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """

    word, translation = message.get_args().split()
    try:
        vocabulary.push(Word(word=word, translation=translation))
        await message.reply("World added")
    except Exception:
        await message.reply("Error")
        raise Exception


@dp.message_handler(commands=['last'], state=words_list)
async def get_words_list(message: types.Message, state: FSMContext):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    try:
        limit = int(message.get_args())
    except Exception:
        limit = 5
    data = vocabulary.get_list(limit)

    print(data)

    await state.set_data([item._id for item in data])
    format_score = lambda score: "{0:.1f}".format(score / 5 * 100)
    output = format_list(data, lambda w: f"{w.word} - {format_score(w.score)}%")
    await message.reply(output)

@dp.message_handler(commands=['mem'], state=words_list)
async def memorize_word(message: types.Message, state: FSMContext):
    all_indexes = await state.get_data()
    try:
        memorable_words_indexes = await getIndexesFromMsg(message, len(all_indexes))
    except InvalidDataError:
        return
    words_in_need_to_repeat = [ wi for index, wi in enumerate(all_indexes, start=1) if not index in memorable_words_indexes ]
    words_to_update_score = [ id for id in all_indexes if not id in words_in_need_to_repeat ]
    vocabulary.update_scores(words_to_update_score)
    words_full_list = vocabulary.get_list(len(all_indexes))

    output = format_list([word for word in words_full_list if word._id in words_in_need_to_repeat], lambda w: f"{w.word} - {w.translation}")
    await message.reply(output)

@dp.message_handler(commands=['del'], state=words_list)
async def delete_words(message: types.Message, state: FSMContext):
    all_indexes = await state.get_data()
    try:
        words_to_delete_indexes = await getIndexesFromMsg(message, len(all_indexes))
    except InvalidDataError:
        return

    words_to_delete = [ wi for index, wi in enumerate(all_indexes, start=1) if index in words_to_delete_indexes ]


    vocabulary.delete_words(words_to_delete)
    await state.set_data([wid for wid in all_indexes if not wid in words_to_delete_indexes])
    await message.reply("Words deleted")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

