import json
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
import emoji
from emoji import demojize

from filters import EmailCheck
from keyboards.big_menu import show_big_menu


class FSMAdmin(StatesGroup):
    user_login = State()
    user_password = State()
    user_task = State()


async def send_welcome(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти в Tasker'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)


async def menu(message: types.Message, state: FSMContext):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text='Войти в Tasker'))
    await message.answer("Вас приветствует бот приложения Tasker", reply_markup=keyboard)
    words_for_menu = ['Выйти из Tasker', '/start']
    if message.text in words_for_menu:
        async with state.proxy() as data:
            pass
        url = 'http://51.250.31.196/api/v1/auth/logout/'
        headers = {'Authorization': data['access_token'], }
        data = {'device_id': 1, }
        requests.post(url, json=data, headers=headers)
    await state.finish()


async def email(message: types.Message):
    await FSMAdmin.user_login.set()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Выйти из Tasker"))
    await message.answer("Введите почту", reply_markup=keyboard)


async def password(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_login'] = message.text
    await FSMAdmin.next()
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.InlineKeyboardButton(text="Выйти из Tasker"))
    await message.answer("Введите пароль", reply_markup=keyboard)


async def sign_in(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_password'] = message.text
    url = 'http://51.250.31.196/api/v1/auth/signin/'
    data = {
        'email': data['user_login'],
        'password': data['user_password'],
        'device_id': 1,
        'device_type': 1,
        'device_name': 1,
        'registration_id': 11111,
    }
    login = requests.post(url, json=data)
    if login.status_code == 200:
        show_big_menu()
        access_token = 'Bearer ' + json.loads(login.content.decode('utf-8'))['access_token']
        async with state.proxy() as data:
            data['access_token'] = access_token
        await message.answer("Вы зашли", reply_markup=show_big_menu())
        await FSMAdmin.next()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.InlineKeyboardButton(text="Войти в Tasker"))
        await message.answer("Данные указаны неверно, проверьте еще раз", reply_markup=keyboard)


async def all_self_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/tab-element/list/?role=4'
    count_task = requests.get(url, headers=headers)
    all_tasks_info = json.loads(count_task.content.decode('utf-8'))['results']
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


async def outgoing_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/tab-element/list/?role=1'
    count_task = requests.get(url, headers=headers)
    all_tasks_info = json.loads(count_task.content.decode('utf-8'))['results']
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


async def finished_outgoing_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/list/?user_roles=1&state=2&limit=10'
    count_task = requests.get(url, headers=headers)
    all_tasks_info = json.loads(count_task.content.decode('utf-8'))
    task_num = 1
    await message.answer("Исходящие - Выполненные, последние 10 задач:", reply_markup=show_big_menu())
    for i in range(len(all_tasks_info['results'])-1):
        await message.answer(text=f"{task_num} - {all_tasks_info['results'][i]['name']}")
        task_num += 1


async def ingoing_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/tab-element/list/?role=3'
    count_task = requests.get(url, headers=headers)
    all_tasks_info = json.loads(count_task.content.decode('utf-8'))['results']
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


async def finished_ingoing_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/list/?limit=10&user_roles=3&state=2,3'
    count_task = requests.get(url, headers=headers)
    all_self_tasks_info = json.loads(count_task.content.decode('utf-8'))
    url2 = 'http://51.250.31.196/api/v1/task/list/?limit=10&user_roles=4&state=2,3'
    count_task2 = requests.get(url2, headers=headers)
    all_ingoing_tasks_info = json.loads(count_task2.content.decode('utf-8'))
    url3 = 'http://51.250.31.196/api/v1/task/list/?limit=10&user_roles=2&state=2,3'
    count_task3 = requests.get(url3, headers=headers)
    all_spectator_tasks_info = json.loads(count_task3.content.decode('utf-8'))
    all_task_info = all_self_tasks_info['results'] + \
                    all_ingoing_tasks_info['results'] + \
                    all_spectator_tasks_info['results']
    all_task_info.sort(key=lambda a: a['updated_at'], reverse=True)
    task_num = 1
    await message.answer("Входящие - Выполненные, последние 10 задач:", reply_markup=show_big_menu())
    for i in range(len(all_task_info)):
        await message.answer(text=f"{task_num} - {all_task_info[i]['name']}")
        task_num += 1
        if task_num == 11:
            break


async def spectator_tasks(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        pass
    show_big_menu()
    headers = {
        'Authorization': data['access_token'],
    }
    url = 'http://51.250.31.196/api/v1/task/tab-element/list/?role=2'
    count_task = requests.get(url, headers=headers)
    all_tasks_info = json.loads(count_task.content.decode('utf-8'))['results']
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


async def settings(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(types.InlineKeyboardButton(text="Назад в меню"),
                 types.InlineKeyboardButton(text="Выйти из Tasker"))
    await message.answer("Вы в настройках", reply_markup=keyboard)


async def main_menu(message: types.Message):
    show_big_menu()
    await message.answer("Главное меню", reply_markup=show_big_menu())


async def self_task(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['user_task'] = message.text
    await message.answer(text=f"Для Вас создана задача - {data['user_task']}")
    url = 'http://51.250.31.196/api/v1/task/'
    headers = {
        'Authorization': data['access_token'],
    }
    data = {
        'name': data['user_task'],
        'user_roles': [],
        'subtasks': [],
        'user_files': []
    }
    requests.post(url, json=data, headers=headers)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start', 'help'], state=None)
    dp.register_message_handler(email, content_types=['text'], text='Войти в Tasker', state='*')
    dp.register_message_handler(menu, content_types=['text'], text=['Выйти из Tasker', '/start'], state='*')
    dp.register_message_handler(password, EmailCheck(), state=FSMAdmin.user_login)
    dp.register_message_handler(sign_in, state=FSMAdmin.user_password)
    dp.register_message_handler(all_self_tasks, content_types=['text'], text=['Личные'],  state='*')
    dp.register_message_handler(outgoing_tasks, content_types=['text'], text=['Исходящие'],  state='*')
    dp.register_message_handler(finished_outgoing_tasks, content_types=['text'], text=['Выполненные'],  state='*')
    dp.register_message_handler(ingoing_tasks, content_types=['text'], text=['Входящие'],  state='*')
    dp.register_message_handler(finished_ingoing_tasks, content_types=['text'], text=['ВхВыполненные'],  state='*')
    dp.register_message_handler(spectator_tasks, content_types=['text'], text=['Участвую'],  state='*')
    dp.register_message_handler(settings, lambda message: demojize(message.text) == ':gear:', state='*')
    dp.register_message_handler(main_menu, content_types=['text'], text=['Назад в меню'], state='*')
    dp.register_message_handler(self_task, content_types=['text'], state=FSMAdmin.user_task)
