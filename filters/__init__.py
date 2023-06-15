from .filters import NeedInt, EmailCheck, DeviceType, RegistrationID
from create import dp

if __name__ == 'filters':
    dp.filters_factory.bind(NeedInt)
    dp.filters_factory.bind(EmailCheck)
    dp.filters_factory.bind(DeviceType)
    dp.filters_factory.bind(RegistrationID)