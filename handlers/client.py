import json
import time

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import emoji


class FSMAdmin(StatesGroup):
    email_login = State()
    email_code = State()
    user_task = State()
    phone_login = State()
    phone_code = State()


async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти по номеру телефона'),
                 types.InlineKeyboardButton(text='Войти через email'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)


async def menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти по номеру телефона'),
                 types.InlineKeyboardButton(text='Войти через email'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)
    words_for_menu = ['Выйти из Tasker', '/start']
    if message.text in words_for_menu:
        async with state.proxy() as data:
            pass
        try:
            url = 'http://51.250.31.196/api/v1/auth/logout/'
            headers = {'Authorization': data['access_token'], }
            data = {'device_id': 1, }
            requests.post(url, json=data, headers=headers)
        except KeyError as e:
            print("Error: ", e)
    await state.finish()


async def email(message: types.Message, state: FSMContext):
    await FSMAdmin.email_login.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Выйти из Tasker"))
    await message.answer("Введите почту", reply_markup=keyboard)


async def email_code(message: types.Message, state: FSMContext):
    if message.text == 'Отправить код повторно':
        await FSMAdmin.email_login.set()
        time.sleep(5)
        async with state.proxy() as data:
            pass
    else:
        async with state.proxy() as data:
            data['email_login'] = message.text
    url = 'http://51.250.31.196/api/v1/auth/code/request/'
    data = {
        "type": 1,
        "value": data['email_login']
    }
    login = requests.post(url, json=data)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text="Отправить код повторно"),
                 types.InlineKeyboardButton(text="Выйти из Tasker"))
    if login.status_code == 200:
        await message.answer("Введите код авторизации. На указанный email отправлен код авторизации", reply_markup=keyboard)
        await FSMAdmin.next()
    else:
        await message.answer("Проверьте указанный email. Код авторизации не отправлен", reply_markup=keyboard)


async def sign_in(message: types.Message, state: FSMContext):
    if message.html_text == 'Отправить код повторно':
        if state.storage.data[str(state.user)][str(state.user)]['state'] == 'FSMAdmin:phone_code':
            await phone_code(message=message, state=state)
        elif state.storage.data[str(state.user)][str(state.user)]['state'] == 'FSMAdmin:email_code':
            await email_code(message=message, state=state)
    else:
        if state.storage.data[str(state.user)][str(state.user)]['state'] == 'FSMAdmin:phone_code':
            async with state.proxy() as data:
                data['phone_code'] = message.text
            data = {
                'value': data['phone_login'],
                'code': data['phone_code'],
                'type': 2,
                'device_id': 1,
                'device_type': 1,
                'registration_id': 11111
            }
        elif state.storage.data[str(state.user)][str(state.user)]['state'] == 'FSMAdmin:email_code':
            async with state.proxy() as data:
                data['email_code'] = message.text
            data = {
                'value': data['email_login'],
                'code': data['email_code'],
                'type': 1,
                'device_id': 1,
                'device_type': 1,
                'registration_id': 11111
            }
        else:
            await message.answer("Используйте доступные команды.")
        try:
            url = 'http://51.250.31.196/api/v1/auth/signin/code/'
            login = requests.post(url, json=data)
            if login.status_code == 200:
                access_token = 'Bearer ' + json.loads(login.content.decode('utf-8'))['access_token']
                async with state.proxy() as data:
                    data['access_token'] = access_token
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.row(types.InlineKeyboardButton(text="Личные задачи"),
                             types.InlineKeyboardButton(text="Выйти из Tasker"))
                await message.answer("Вы зашли", reply_markup=keyboard)
                await FSMAdmin.user_task.set()
            else:
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                keyboard.add(types.InlineKeyboardButton(text="Войти в Tasker"))
                await message.answer("Код введен неверно, попробуйте ещё раз.", reply_markup=keyboard)
        except Exception as e:
            print("Error: ", e)


async def self_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_task'] = message.text
    try:
        url = 'http://51.250.31.196/api/v1/task/'
        headers = {
            'Authorization': data['access_token'],
        }
        data_response = {
            'name': data['user_task'],
            'user_roles': [],
            'subtasks': [],
            'user_files': []
        }
        add_task = requests.post(url, json=data_response, headers=headers)
        if add_task.status_code == 201:
            await message.answer(text=f"Для Вас создана задача - {data['user_task']}")
    except:
        await message.answer(text=f"Задача не создалась - {data['user_task']}")


async def all_self_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    try:
        headers = {
            'Authorization': data['access_token'],
        }
        url = 'http://51.250.31.196/api/v1/task/tab-element/list/?role=4'
        count_task = requests.get(url, headers=headers)
        all_tasks_info = json.loads(count_task.content.decode('utf-8'))['results']
        if not all_tasks_info:
            await message.answer(text="У Вас нет личных задач")
        all_folders = []
        only_tasks = [task for task in all_tasks_info if task['task'] is not None]
        for j in all_tasks_info:
            folder = j['folder']
            if folder is not None and folder['name'] not in all_folders:
                await message.answer(text=f"{emoji.emojize(':file_folder:')} {folder['name']}")
                tasks_in_folder = [await message.answer(text=f"l_{u['task']['name']}") for u in only_tasks if folder['name'] == u['task']['folder']]
                all_folders.append(folder['name'])
            elif j['task']['folder'] in all_folders:
                pass
            else:
                await message.answer(text=f"{j['task']['name']}")
    except KeyError as err:
        await message.answer(text=f"Ошибка: {err}, надо зайти заново")
    except Exception as e:
        print("error: ", e)



async def phone(message: types.Message, state: FSMContext):
    await FSMAdmin.phone_login.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Выйти из Tasker"))
    await message.answer("Введите номер телефона", reply_markup=keyboard)


async def phone_code(message: types.Message, state: FSMContext):
    if message.text == 'Отправить код повторно':
        await FSMAdmin.phone_login.set()
        time.sleep(5)
        async with state.proxy() as data:
            pass
    else:
        async with state.proxy() as data:
            data['phone_login'] = message.text
    url = 'http://51.250.31.196/api/v1/auth/code/request/'
    data = {
        "type": 2,
        "value": data['phone_login']
    }
    login = requests.post(url, json=data)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text="Отправить код повторно"),
                 types.InlineKeyboardButton(text="Выйти из Tasker"))
    if login.status_code == 200:
        await message.answer("Введите код авторизации. На указанный номер телефона отправлен код", reply_markup=keyboard)
        await FSMAdmin.next()
        print("2")
    else:
        await message.answer("Проверьте указанный номер телефона. Код авторизации не отправлен."
                             " Введите номер телефона в международном формате начиная с +...", reply_markup=keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'], state=None)
    dp.register_message_handler(menu, content_types=['text'], text=['Войти в Tasker', 'Выйти из Tasker', '/start'], state='*')
    dp.register_message_handler(email, content_types=['text'], text='Войти через email', state='*')
    dp.register_message_handler(phone, content_types=['text'], text='Войти по номеру телефона', state='*')
    dp.register_message_handler(email_code, content_types=['text'], state=FSMAdmin.email_login)
    dp.register_message_handler(phone_code, content_types=['text'], state=FSMAdmin.phone_login)
    dp.register_message_handler(all_self_tasks, content_types=['text'], text=['Личные задачи'],  state='*')
    dp.register_message_handler(self_task, content_types=['text'], state=FSMAdmin.user_task)
    dp.register_message_handler(sign_in, content_types=['text'], state='*')
