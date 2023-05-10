from db import DBBot
from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio


class FSMAdmin(StatesGroup):
    site = State()
    login = State()
    password = State()


class FSMDel(StatesGroup):
    del_login = State()


class FSMGet(StatesGroup):
    get_login = State()


TOKEN = '5916297594:AAFdxsRXD4AyGDaJsMdlm006v_w5rL3ERxg'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
BotDB = DBBot('storage.db')


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    if not BotDB.user_exists(message.from_user.id):
        BotDB.add_user(message.from_user.id)
    await message.bot.send_message(message.from_user.id, "Добро пожаловать. Я бот для хранения паролей.\n"
                                                         "Список доступных команд:\n"
                                                         "/set - добавить сайт и задать для него лоигн и пароль\n"
                                                         "/get - получить полгин и пароль для добавленного "
                                                         "ранее сайта\n"
                                                         "/del - удалить сайт из списка")


@dp.message_handler(commands='set')
async def set_site(message: types.Message):
    await FSMAdmin.site.set()
    await message.bot.send_message(message.from_user.id, 'Введи название сайта')


@dp.message_handler(state=FSMAdmin.site)
async def set_site(message: types.Message, state: FSMContext):
    if BotDB.site_exists(message.from_user.id, message.text):
        await message.bot.send_message(message.from_user.id, 'Логин для такого сайта'
                                                             'уже существует. введи другое название сайта '
                                                             'или удали существующее и создай новую запись')
    elif message.text[0][0] == '/':
        await message.bot.send_message(message.from_user.id, 'Некорректное название сайта')
    else:
        await state.update_data(site=message.text)
        await message.bot.send_message(message.from_user.id, f'Введи логин для сайта {message.text}')
        await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.login)
async def set_site(message: types.Message, state: FSMContext):
    data = await state.get_data()
    site = data.get('site')
    await state.update_data(login=message.text)
    await message.bot.send_message(message.from_user.id, f'Введи пароль для сайта {site}')
    await FSMAdmin.next()


@dp.message_handler(state=FSMAdmin.password)
async def set_site(message: types.Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    site, login, password = data.get('site'), data.get('login'), data.get('password')
    BotDB.add_login(message.from_user.id, site, login, password)
    msg = await message.bot.send_message(message.from_user.id, f'Создана запись:\n'
                                                               f'Сайт: {site}\n'
                                                               f'Логин: {login}\n'
                                                               f'Пароль: {password}')
    await state.finish()
    await asyncio.sleep(10)
    try:
        await message.delete()
        await msg.delete()
    except Exception:
        pass


@dp.message_handler(commands='del')
async def set_site(message: types.Message):
    await FSMDel.del_login.set()
    await message.bot.send_message(message.from_user.id, 'Введи название сайта, который хочешь удалить')


@dp.message_handler(state=FSMDel.del_login)
async def set_site(message: types.Message, state: FSMContext):
    await state.update_data(del_login=message.text)
    data = await state.get_data()
    del_login = data.get('del_login')
    BotDB.del_login(message.from_user.id, del_login)
    await message.bot.send_message(message.from_user.id, f'Сайт {del_login} удален из списка')
    await state.finish()


@dp.message_handler(commands='get')
async def set_site(message: types.Message):
    await FSMGet.get_login.set()
    await message.bot.send_message(message.from_user.id, 'Введи название сайта, '
                                                         'информацию о котором хочешь просмотреть')


@dp.message_handler(state=FSMGet.get_login)
async def set_site(message: types.Message, state: FSMContext):
    await state.update_data(get_login=message.text)
    data = await state.get_data()
    get_login = data.get('get_login')
    result = BotDB.get_info(message.from_user.id, get_login)
    if len(result) > 0:
        msg = await message.bot.send_message(message.from_user.id, f'Логин: {result[0][0]}\n'
                                                                   f'Пароль: {result[0][1]}')
        await asyncio.sleep(10)
        try:
            await msg.delete()
        except Exception:
            pass
        await state.finish()
    else:
        await message.bot.send_message(message.from_user.id, 'Такого сайта нет в твоем списке')
        await state.finish()




if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
