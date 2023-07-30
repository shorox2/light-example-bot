from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

TOKEN_API = '5922984473:AAGgmxZFUPnyhtbjlhQpI1HxNdO78wBxw18'
storage = MemoryStorage() # ЛОКАЛЬНОЕ ХРАНИЛИЩЕ
bot = Bot(TOKEN_API)
dp = Dispatcher(bot, storage = storage) # ЛОКАЛЬНОЕ ХРАНИЛИЩЕ

# МОИ СОСТОЯНИЯ
class ProfileStatesGroup(StatesGroup):
    photo = State()
    name = State()
    age = State()
    description = State()


async def on_startup(_):
    print('WIN!!!')

def get_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('/create'))
    return kb

def get_cancel_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add('/cancel')
    return kb

@dp.message_handler(commands=['cancel'], state='*') # * - ЛЮБОЕ СОСТОЯНИЕ
async def cancel_profile_cmd(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await message.answer('ВЫ ПРЕРВАЛИ СОЗДАНИЕ АНКЕТЫ'.lower(), reply_markup=get_kb())


@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    await message.answer('Привет! ЧТОБЫ СОЗДАТЬ ПРОФИЛЬ НАЖМИ НА КНОПКУ'.lower(), reply_markup=get_kb())

@dp.message_handler(commands=['create'])
async def create_cmd(message: types.Message):
    await message.reply('ОтЛИЧНО, ДАВАЙ НАЧНЕМ СОЗДАВАТЬ ТВОй ПРОФИЛЬ, ДЛЯ НАЧАЛА ОТПРАВЬ МНЕ СВОЮ ФОТОГРАФИЮ!'.lower(), reply_markup=get_cancel_kb())
    await ProfileStatesGroup.photo.set()

# ПРОВЕРКА ЕСЛИ НЕ ФОТО
@dp.message_handler(lambda message: not message.photo, state=ProfileStatesGroup.photo)
async def check_photo(message: types.Message):
    await message.reply('ЭТО НЕ ФОТОГРАФИЯ!!!')

@dp.message_handler(content_types=['photo'], state= ProfileStatesGroup.photo)
async def wait_photo_cmd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['photo'] = message.photo[0].file_id

    await message.reply('ТЕПЕРЬ ОТПРАВЬ СВОЕ ИМЯ!'.lower())
    await ProfileStatesGroup.next()
# ПРОВЕРКА ЕСЛИ МЕНЬШЕ 3 БУКВ
@dp.message_handler(lambda message: not message.text or len(message.text) <= 3, state=ProfileStatesGroup.name)
async def check_photo(message: types.Message):
    await message.reply('НОРМАЛЬНОГО ЧЕЛОВЕКА МЕНЬШЕ ЧЕМ ИЗ 3 БУКВ НЕ НАЗОВУТ!')

@dp.message_handler(state= ProfileStatesGroup.name)
async def wait_name_cmd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

    await message.reply('СКОЛЬКО ТЕБЕ ЛЕТ?'.lower())
    await ProfileStatesGroup.next()

# ПРОВЕРКА на ВОЗРАСТ
@dp.message_handler(lambda message: not message.text.isdigit() or float(message.text) < 0 or float(message.text) > 100, state=ProfileStatesGroup.age)
async def check_photo(message: types.Message):
    await message.reply('НЕ МОРОСИ ДА')

@dp.message_handler(state= ProfileStatesGroup.age)
async def wait_age_cmd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['age'] = message.text

    await message.reply('РАССКАЖИ НЕМНОГО О СЕБЕ'.lower())
    await ProfileStatesGroup.next()

@dp.message_handler(state= ProfileStatesGroup.description)
async def wait_desc_cmd(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = message.text
        await bot.send_photo(chat_id=message.from_user.id, photo=data['photo'], caption=f"<b>{data['name']} {data['age']}</b>\n{data['description']}", parse_mode='HTML')

    await message.answer('ВАША АНКЕТА УСПЕШНО СОЗДАНА!'.lower(), reply_markup=ReplyKeyboardRemove())
    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)