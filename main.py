import asyncio
import datetime
import logging
import sys

import requests
import fake_useragent
from bs4 import BeautifulSoup, SoupStrainer

from aiogram import Bot, Dispatcher, html
from aiogram import Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from random import randint
import data


TOKEN = ''


dp = Dispatcher()

router = Router()

kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Узнать')],
        [KeyboardButton(text='Настройки')]
    ],
    resize_keyboard=True
)
def get_result(name : str, surname : str, document: int, getuser : bool):
    user = fake_useragent.UserAgent().random
    if getuser == True:
        return user
    else:
        url = 'https://result.rcoi25.ru/'
        headers = {
            'User-Agent': user,
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        session = requests.Session()
        r = session.get(url, headers=headers)
        token = BeautifulSoup(r.content, 'html.parser').findAll('input')[-1]['value']

        datas = {
            "form[name]": name,
            "form[surname]": surname,
            "form[document]": document,

            "form[_token]": token
        }

        r = session.post(url, headers=headers, data=datas)
        soup = BeautifulSoup(r.content, 'html.parser')
        g = list(soup.findAll('tr'))
        res = []
        for i in range(len(g)):
            res.append(str(g[i]).replace('<th>', '').replace('</th>', '').replace('<td>', '').
                       replace('</td>', '').replace('<tr class="table-success">', '').replace('<tr>', '').
                       replace('</tr>', '').replace(
                '[<tr><th>Дата</th><th>Предмет</th><th>Место проведения</th><th>Тестовый балл</th><th>Статус результата</th><th>Подробности</th>',
                '').
                       replace('<tr class="table-warning">', ''))
        return ', '.join(map(str, res[1:len(res)])).replace(',', '')
# @dp.message(CommandStart())
# async def command_start_handler(message: Message) -> None:
#     await message.answer(f"Здравсвуйте, {html.bold(message.from_user.full_name)}!\nНажимая {html.bold('Далее')} вы даёте согласие на обработку персональных данных", reply_markup=kb)
@dp.message(CommandStart())
async def cmd_random(message: Message):
    await message.bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="Далее",
        callback_data="random_value")
    )
    await message.answer(
         f"Здравствуйте, {html.bold(message.from_user.full_name)}!",
        reply_markup=ReplyKeyboardRemove()
    )
    await message.answer(
        f"Нажимая {html.bold('Далее')} вы даёте согласие на обработку ваших персональных данных",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "random_value")
async def send_random_value(callback: CallbackQuery):
    await callback.message.bot.delete_message(message_id=callback.message.message_id, chat_id=callback.message.chat.id)
    await callback.message.answer('Спасибо, что выбрали нас ❤️', reply_markup=kb)
    await callback.answer(
        text="Разбработанное ПО не является офицальным продуктом РЦОИ Приморья",
        show_alert=True
    )
@router.message(Command('test'))
async def command_test_handler(message: Message) -> None:
    await message.answer(f"Hello, {html.bold(message.from_user.full_name)}!", reply_markup=kb)
    await message.answer(str(data.build()))

@router.message(F.text == 'Узнать')
async def getres(message: Message, state: FSMContext):
    user = data.build()
    print(user)
    if message.chat.id not in user:
        await message.answer("Щас я тебя в книжечку запишу")
        await cmd_food(message, state)
    else:
        await message.answer(f'Актуально на {datetime.datetime.now()}')
        user = data.build()
        await message.answer(get_result(user[message.chat.id]['name'], user[message.chat.id]['surname'], int(user[message.chat.id]['document']), False))
        await message.answer('Поздравляю!')


@router.message(F.text == 'Настройки')
async def getsettings(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user = get_result(None, None, None, getuser=True)
    await message.answer(f'Время на сервере {datetime.datetime.now()}\nАгент {user}')
    try:
        await message.answer(f"Я на тебя тут нарыл: \n{user_data['name']}\n{user_data['surname']}\n{user_data['document']}")
    except KeyError:
        await message.answer('Данных нет!')
class OrderFood(StatesGroup):
    name = State()
    surname = State()
    document = State()


@router.message(F.text == 'Тест')
async def cmd_food(message: Message, state: FSMContext):
    await message.answer(
        text="Пиши две буквы имени"
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(OrderFood.name)

# Этап выбора блюда #


@router.message(OrderFood.name)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(name=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, фамилию, три буквы"
    )
    await state.set_state(OrderFood.surname)


@router.message(OrderFood.surname)
async def food_size_chosen(message: Message, state: FSMContext):
    await state.update_data(surname=message.text.lower())
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, документ"
    )

    await state.set_state(OrderFood.document)

@router.message(OrderFood.document)
async def food_chosen(message: Message, state: FSMContext):
    await state.update_data(document=int(message.text))
    user_data = await state.get_data()
    await message.answer(
         text=f"Проверяй \n{user_data['name']}\n{user_data['surname']}\n{message.text}"
    )
    data.create(message.chat.id, user_data['name'], user_data['surname'], message.text)
    await state.set_data(user_data)
    await getres(message, state)
    await state.clear()


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
