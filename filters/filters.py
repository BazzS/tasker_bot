from aiogram.dispatcher.filters import BoundFilter
from aiogram import types
import re

regex_email = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'


class NeedInt(BoundFilter):
    async def check(self, obj: types.Message):
        data = obj.text
        if data.isdigit():
            return True
        else:
            await obj.answer("Нужно число")
        return False


class EmailCheck(BoundFilter):
    async def check(self, obj: types.Message):
        data = obj.text
        if re.fullmatch(regex_email, data):
            return True
        else:
            await obj.answer("Введите правильный email адрес")
        return False


class DeviceType(BoundFilter):
    async def check(self, obj: types.Message):
        data = obj.text
        if data.isdigit():
            if int(data) == 1 or int(data) == 2 or int(data) == 3:
                return True
            else:
                await obj.answer("Введите правильный тип устройства")
        else:
            await obj.answer("Тип устройства обозначается числом")
        return False


class RegistrationID(BoundFilter):
    async def check(self, obj: types.Message):
        data = obj.text
        if len(data) == 5:
            return True
        else:
            await obj.answer("Регистрационный id состоит из 5 цифер")
        return False


