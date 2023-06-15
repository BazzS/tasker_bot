from aiogram import executor
from create import dp
from handlers import client_local


async def on_startup(_):
    print("Бот запустился")

client_local.register_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
