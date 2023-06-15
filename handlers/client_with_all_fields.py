from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from filters import EmailCheck, NeedInt, DeviceType, RegistrationID


class FSMAdmin(StatesGroup):
    user_login = State()
    user_password = State()
    device_id = State()
    device_type = State()
    device_name = State()
    registration_id = State()
    #access_token = State()
    user_task = State()


async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти в Tasker'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)


async def main_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти в Tasker'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)


async def email(message: types.Message, state: FSMContext):
    await FSMAdmin.user_login.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите почту", reply_markup=keyboard)


async def password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_login'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите пароль", reply_markup=keyboard)
    print(data['user_login'])


async def device_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_password'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите id устройства", reply_markup=keyboard)
    print(data['user_password'])


async def device_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['device_id'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите тип устройства", reply_markup=keyboard)
    print(data['device_id'])


async def device_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['device_type'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите имя устройства", reply_markup=keyboard)
    print(data['device_type'])


async def registration_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['device_name'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
    await message.answer("Введите id регистрации", reply_markup=keyboard)
    print(data['device_name'])


async def sign_in(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['registration_id'] = message.text
    #await FSMAdmin.next()
    print(data['registration_id'])
    url = 'http://127.0.0.1:8080/api/v1/auth/signin/'
    data = {
        'email': data['user_login'],
        'password': data['user_password'],
        'device_id': data['device_id'],
        'device_type': data['device_type'],
        'device_name': data['device_name'],
        'registration_id': data['registration_id'],
    }
    login = requests.post(url, json=data)
    print(login)
    access_token = 'Bearer ' + login.content.decode('UTF-8')[100:-2]
    async with state.proxy() as data:
        data['access_token'] = access_token
    if login.status_code == 200:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Выйти из аккаунта"))
        await message.answer("Вы зашли", reply_markup=keyboard)
        await FSMAdmin.next()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="В главное меню"))
        await message.answer("Данные указаны неверно, проверьте еще раз", reply_markup=keyboard)


async def self_task(message: types.Message, state: FSMContext):
    #await FSMAdmin.user_task.set()
    async with state.proxy() as data:
        data['user_task'] = message.text
    print(data['user_task'])
    if data['user_task'] == "Выйти из аккаунта":
        url = 'http://127.0.0.1:8080/api/v1/auth/logout/'
        headers = {
            'Authorization': data['access_token'],
        }
        data = {
            'device_id': data['device_id'],
        }
        user_logout = requests.post(url, json=data, headers=headers)
        print(user_logout)
        await state.finish()
    else:
        url = 'http://127.0.0.1:8080/api/v1/task/'
        headers = {
            'Authorization': data['access_token'],
        }
        data = {
            'name': data['user_task'],
            'user_roles': [],
            'subtasks': [],
            'user_files': []
        }
        new_task = requests.post(url, json=data, headers=headers)
        print(new_task)
    url2 = 'http://127.0.0.1:8080/api/v1/task/list/'
    count_task = requests.get(url2, headers=headers)
    start_count = count_task.content.decode('UTF-8').find(':') + 1
    finish_count = count_task.content.decode('UTF-8').find(',')
    all_tasks = count_task.content.decode('UTF-8')[start_count:finish_count]
    print(all_tasks)
    await state.finish()


# async def logout(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         pass
#     url = 'http://127.0.0.1:8080/api/v1/auth/logout/'
#     headers = {
#         'Authorization': data['access_token'],
#     }
#     data = {
#         'device_id': data['device_id'],
#     }
#     user_logout = requests.post(url, json=data, headers=headers)
#     print(user_logout)
#     await state.finish()



def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'], state=None)
    dp.register_message_handler(email, content_types=['text'], text='Войти в Tasker', state='*')
    dp.register_message_handler(main_menu, content_types=['text'], text=['В главное меню', 'Выйти из аккаунта'], state='*')
    dp.register_message_handler(password, EmailCheck(), state=FSMAdmin.user_login)
    dp.register_message_handler(device_id, state=FSMAdmin.user_password)
    dp.register_message_handler(device_type, NeedInt(), state=FSMAdmin.device_id)
    dp.register_message_handler(device_name, DeviceType(), state=FSMAdmin.device_type)
    dp.register_message_handler(registration_id, state=FSMAdmin.device_name)
    dp.register_message_handler(sign_in, RegistrationID(), state=FSMAdmin.registration_id)
    dp.register_message_handler(self_task, content_types=['text'], state=FSMAdmin.user_task)
    #dp.register_message_handler(logout, content_types=['text'], text='Выйти из аккаунта', state='*')


