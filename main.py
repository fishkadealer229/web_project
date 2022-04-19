import logging
import os
import sqlite3
from time import sleep

from config import token
from aiogram import Bot, Dispatcher, executor, types
bot = Bot(token=token)
dp = Dispatcher(bot)
db_values = []
register_flag = False
admin_flag = False
search_flag = False
update_flag = False
new_value = True
flag = False
flag1 = True
flag2 = False
password = ''
update_value = ''
count_values = 1
last_username = ''
blank_values = ["Имя Фамилия", "Пол", "Юзернейм", 'Должность', "Фотография"]
requests = ['своё имя и фамилию', 'свой пол', 'свой юзернейм', "свою должность в компании",
            'свою фотографию для профиля']
ind = 0
logging.basicConfig(level=logging.INFO)
con = sqlite3.connect('meetings_data.db')
cur = con.cursor()


@dp.message_handler(commands=['start'])
async def begin(message: types.Message):
    if register_flag:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.insert(types.InlineKeyboardButton(text='Да', callback_data='search'))
        keyboard.insert(types.InlineKeyboardButton(text='Нет', callback_data='ok'))
        await message.answer('Хотите кого-то найти?', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.insert(types.InlineKeyboardButton(text='Войти в обычный аккаунт', callback_data='common'))
        keyboard.insert(types.InlineKeyboardButton(text='Войти в аккаунт админа', callback_data='admin'))
        await message.answer('Здравствуйте! Я бот для связи между сотрудниками одной компании, созданный компанией'
                             ' "Нигэз Студио".', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('''Хотите войти в обычный аккаунт или в аккаунт админа?''', reply_markup=keyboard)


@dp.message_handler(commands=['menu'])
async def menu(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(text='Зарегестрироваться как администратор', callback_data='admin'))
    keyboard.insert(types.InlineKeyboardButton(text='Зарегестрироваться как сотрудник', callback_data='common'))
    keyboard.add(types.InlineKeyboardButton(text='Поиск', callback_data='search'))
    keyboard.add(types.InlineKeyboardButton(text='Изменить свою анкету', callback_data='update_blank'))
    await message.answer('Вот, что может этот ботяра.', reply_markup=keyboard)


@dp.message_handler(commands=['help'])
async def help1(message: types.Message):
    await message.answer('Что!?')
    sleep(2)
    await message.answer('Кому то реально понадобилась помощь в этом наилегчайшем ботяре?')
    sleep(2)
    await message.answer('OK. Просто почитайте книгу "workerStuffBot для чайников"')
    sleep(2)
    await message.answer('Бесят уже эти кожанные 👿 👿 👿 👿')


@dp.callback_query_handler(text='common')
async def register_asks(call: types.CallbackQuery):
    global requests, ind
    telegram_values = [call.from_user.first_name + " " + call.from_user.last_name, 'Мужчина', call.from_user.username,
                       '', '', '']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if ind <= 2:
        keyboard.add(types.KeyboardButton(text=f'{telegram_values[ind]}'))
    if ind == 1:
        keyboard.add(types.KeyboardButton(text='Женщина'))
    if ind < len(requests):
        await call.message.answer(f'Укажите {requests[ind]}', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='update_blank'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='end_register'))
        await call.message.answer('Хотите изменить анкету?', reply_markup=keyboard)
        await call.answer('Ввод данных пользователем')


@dp.callback_query_handler(text='admin')
async def admin_register(call: types.CallbackQuery):
    global blank_values, admin_flag
    admin_flag = True
    blank_values.insert(3, "Пароль")
    requests.insert(3, "свой пароль")
    await register_asks(call)


@dp.callback_query_handler(text='update_blank')
async def update_blank(call: types.CallbackQuery):
    global blank_values, update_flag, register_flag, search_flag, flag1
    register_flag = False
    search_flag = False
    update_flag = True
    flag1 = True
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in blank_values:
        keyboard.add(types.KeyboardButton(text=f'{i}'))
    await call.message.answer('Что вас не устраивает?', reply_markup=keyboard)
    await call.answer('Изменение анкеты')


@dp.callback_query_handler(text='end_register')
async def end_register(call: types.CallbackQuery):
    global register_flag, admin_flag, update_flag, search_flag
    register_flag = True
    search_flag = False
    update_flag = False
    name, surname = db_values[0].split()
    path = f'\\photos\\{call.message.chat.id}.jpg'
    if admin_flag:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Перейти к регистрации на сайте', url='https://github.com/'))
        await call.message.answer('Вот ссылка.'
                                  ' Там вам нужно будет войти по юзернейму и паролю, которые вы здесь ввели.',
                                  reply_markup=types.ReplyKeyboardRemove())
        await call.message.answer('Удачи!', reply_markup=keyboard)
        cur.execute(fr'''insert into users (name_surname, gender, username, profession, chat_id, photo_path, password) 
        values("{name + ' ' + surname}", "{db_values[1]}", "{db_values[2]}", "{db_values[3]}", "{call.message.chat.id}",
"{os.getcwd() + path}", "{db_values[4]}")''')
        con.commit()
    else:
        cur.execute(fr'''insert into users (name_surname, gender, username, profession, chat_id, photo_path, password) 
                values("{name + ' ' + surname}", "{db_values[1]}", "{db_values[2]}", "{db_values[3]}",
                 "{call.message.chat.id}", "{os.getcwd() + path}")''')
        con.commit()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.insert(types.InlineKeyboardButton(text='Да', callback_data='search'))
    keyboard.insert(types.InlineKeyboardButton(text='Нет', callback_data='ok'))
    await call.message.answer('Хотите кого-то найти?', reply_markup=keyboard)
    await call.answer('Поиск...')


@dp.callback_query_handler(text='search')
async def search(call: types.CallbackQuery):
    global search_flag, register_flag, update_flag
    search_flag = True
    register_flag = False
    update_flag = False
    await call.message.answer("Введите данные для поиска (Имя Фамилия или должность)")


@dp.callback_query_handler(text='ok')
async def ok(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Искать кого-то...', callback_data='search'))
    await call.message.answer('Ну ок...', reply_markup=keyboard)
    await call.answer('OK')


@dp.message_handler(content_types=['text'])
async def db_insert(message: types.Message):
    global db_values, register_flag, search_flag, update_flag, flag1, flag2, new_value, update_value
    if register_flag:
        await message.reply('Эу нормально общайся. ОК?')
    elif search_flag:
        for value in ['name_surname', 'profession']:
            if (message.text,) in list(cur.execute(f'''select {value} from users''')):
                username = '@' + list(cur.execute(f'select username from users where {value}="{message.text}"'))[0][0]
                await message.answer(f'Вот его юзернейм: {username}')
                break
            else:
                await message.answer('К сожалению, по эти данным ничего не найдено:(')
    elif update_flag:
        new_value = True
        if new_value and message.text in blank_values:
            update_value = message.text
            new_value = False
            flag1 = True
        else:
            if flag1:
                db_values[blank_values.index(update_value)] = message.text
                flag1 = False
            else:
                flag2 = True
        if flag1:
            if message.text != "Фотография":
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
                keyboard.add(types.KeyboardButton(text=f'{db_values[blank_values.index(update_value)]}'))
                await message.answer('Введите новое значение.', reply_markup=keyboard)
            else:
                await message.answer('Отлично', reply_markup=types.ReplyKeyboardRemove())
                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(types.InlineKeyboardButton(text='Оставить прежнию', callback_data='next_data'))
                await message.answer('Отправьте новую фотографию', reply_markup=keyboard)
        else:
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='update_blank'))
            keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='end_register'))
            await message.answer('Ваши данные успешно сохранены', reply_markup=types.ReplyKeyboardRemove())
            await message.answer('Хотите ещё что-нибудь изменить?', reply_markup=keyboard)
    else:
        if message.text.isdigit():
            db_values.append(int(message.text))
        else:
            db_values.append(message.text)
    if flag2:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='end_register'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='update_blank'))
        await message.answer('Отлично', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Закончим регистрацию?', reply_markup=keyboard)
    elif not update_flag or (not flag1 and not new_value and flag2 and not search_flag):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='next'))
        keyboard.add(types.InlineKeyboardButton(text='Конечно', callback_data='next'))
        await message.answer('Отлично', reply_markup=types.ReplyKeyboardRemove())
        await message.answer('Продолжаем?', reply_markup=keyboard)


@dp.callback_query_handler(text='next')
async def next1(call: types.CallbackQuery):
    global ind, count_values, db_values
    if count_values == len(db_values):
        ind += 1
        await register_asks(call)
        await call.answer('next_data')
        count_values += 1
    else:
        await call.answer('Вы ещё не ответили на прошлый вопрос')


@dp.callback_query_handler(text='next_data')
async def next_data(call: types.CallbackQuery):
    await call.message.answer('OK')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='end_register'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='update_blank'))
    await call.message.answer('Отлично', reply_markup=types.ReplyKeyboardRemove())
    await call.message.answer('Закончим регистрацию?', reply_markup=keyboard)


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message: types.Message):
    global update_flag, last_username
    await message.answer(await message.photo[-1].download(f'\\photos\\{message.chat.id}.jpg'))
    await message.answer('Ваше фото успешно сохранено.')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='update_blank'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='end_register'))
    if update_flag:
        await message.answer('Хотите ещё что-нибудь изменить?', reply_markup=keyboard)
    else:
        await message.answer('Хотите изменить анкету?', reply_markup=keyboard)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
