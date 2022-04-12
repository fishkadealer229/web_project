import logging
import sqlite3
from config import token
from aiogram import Bot, Dispatcher, executor, types
bot = Bot(token=token)
dp = Dispatcher(bot)
db_values = []
authorization_flag = False
username_flag = True
password = ''
blank_values = ["Имя", "Фамилия", "Возраст", "Пол", "Адрес проживания", "Адрес работы", "Юзернейм", "Фотография",
                "Пароль"]
requests = ['своё имя', 'свою фамилию', 'свой возраст', 'свой пол', 'свой адрес проживания', 'свой адрес работы',
            'свой юзернейм', 'свою фотографию для профиля']
ind = 0
logging.basicConfig(level=logging.INFO)
con = sqlite3.connect('meetings_data.db')
cur = con.cursor()


@dp.message_handler(commands='start')
async def begin(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.insert(types.InlineKeyboardButton(text='Зарегистрироваться', callback_data='register_asks'))
    keyboard.insert(types.InlineKeyboardButton(text='Войти в свой аккаунт', callback_data='authorization'))
    await message.answer('''Здравствуйте! Я бот для связи между , созданный компанией "Нигэз Студио".
     Хотите зарегистрироваться или войти?''', reply_markup=keyboard)


@dp.callback_query_handler(text='authorization')
async def authorization(call: types.CallbackQuery):
    global authorization_flag, username_flag
    authorization_flag = True
    if username_flag:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        keyboard.insert(types.KeyboardButton(text=f'{call.message.from_user.username}'))
        await call.message.answer('OK. Введите свой "username" (это тот, что с символом "@" в начале)',
                                  reply_markup=keyboard)
        await call.answer('Ввод пользовательского имени')
        username_flag = False
    else:
        await call.message.answer('Введите свой пароль')
        await call.answer('Ввод пароля пользователя')


@dp.callback_query_handler(text='register_asks')
async def register_asks(call: types.CallbackQuery):
    global requests, ind
    telegram_values = [call.from_user.first_name, call.from_user.last_name, '', 'Мужчина', '', '',
                       call.from_user.username, '', '']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    if ind != 2 or 4 <= ind <= 6 or ind != 8 or ind != 9:
        keyboard.add(types.KeyboardButton(text=f'{telegram_values[ind]}'))
    if ind == 3:
        keyboard.add(types.KeyboardButton(text='Женщина'))
    if ind < len(requests):
        await call.message.answer(f'Укажите {requests[ind]}', reply_markup=keyboard)
    else:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text='Да', callback_data='update_blank'))
        keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data='end_register'))
        await call.message.answer('Хотите изменить анкету?', reply_markup=keyboard)
        await call.answer('Ввод данных пользователем')


@dp.callback_query_handler(text='update_blank')
async def update_blank(call: types.CallbackQuery):
    global blank_values
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for i in blank_values:
        keyboard.add(types.KeyboardButton(text=i))
    await call.message.answer('Что вас не устраивает?', reply_markup=keyboard)
    await call.answer('Изменение анкеты')


@dp.callback_query_handler(text='end_register')
async def end_register(call: types.CallbackQuery):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Нажмите для начала авторизации', callback_data='authorization'))
    await call.message.answer('Вы успешно зарегистрировались. Теперь авторизуйтесь', reply_markup=keyboard)
    await call.answer('Авторизация после регистрации')


@dp.message_handler(content_types=['text'])
async def db_insert(message: types.Message):
    global db_values, ind, authorization_flag, username_flag, password
    await message.answer('Отлично', reply_markup=types.ReplyKeyboardRemove())
    if authorization_flag:
        if username_flag:
            password = cur.execute(f'select password from users where username = {message.text}').fetchall()[0]
        else:
            if password == message.text:
                await message.answer('Вход успешно выполнен!')
        callback_data = 'authorization'
    else:
        if message.text.isdigit():
            if ind < len(db_values):
                db_values[ind] = int(message.text)
            else:
                db_values.append(int(message.text))
        else:
            if ind < len(db_values):
                db_values[ind] = message.text
            else:
                db_values.append(message.text)
        ind += 1
        callback_data = 'register_asks'
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=callback_data))
    await message.answer('Хотите продолжить?', reply_markup=keyboard)


@dp.message_handler(content_types=['photo'])
async def photo(message: types.Message):
    file_info = await bot.get_file(message.photo[-1].file_id)
    await message.photo[-1].download(file_info.file_path.split('photos/')[1])
    if ind < len(db_values):
        db_values[ind] = file_info
    else:
        db_values.append(file_info)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
