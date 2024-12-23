import asyncio
import aiogram.types
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from pathlib import Path
import crud_functions

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

crud_functions.initiate_db() # создаем и заполняем базу данных
base_db = crud_functions.get_all_products() # получаем список всех продуктов

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
button1 = KeyboardButton(text='Рассчитать')
button2 = KeyboardButton(text='Информация')
button3 = KeyboardButton(text='Купить')
kb.add(button1, button2)
kb.add(button3)
rm=aiogram.types.ReplyKeyboardRemove()

kb_inline = aiogram.types.InlineKeyboardMarkup()
button_il = aiogram.types.InlineKeyboardButton(text='Формулы расчёта', callback_data= 'formulas')
button_il2 = aiogram.types.InlineKeyboardButton(text='Рассчитать норму калорий', callback_data= 'calories')
kb_inline.add(button_il2, button_il)

kb_inline_buy = aiogram.types.InlineKeyboardMarkup(row_width=4)
button_il_dyn = {}
for i in base_db: # берет из базы продукты
    button_il_dyn[i] = aiogram.types.InlineKeyboardButton(text=f'{i[0]}', callback_data="product_buying") # называет
    # кнопки по названиям продуктов
kb_inline_buy.add(*button_il_dyn.values())


def get_file_paths_pattern(directory, pattern="*"):
    return [str(path) for path in Path(directory).rglob(pattern)]

@dp.message_handler(text='Купить')
async def get_buying_list(message):
    jpg_files = iter(get_file_paths_pattern('./pict', '*.jpg')) # обходим все картинки, у меня 4 шт.
    for prod in base_db: # перебираем все товары, в ходе многократных запусков их больше чем 4
        text_product = f"Название: {prod[0]} | Описание: {prod[1]} | Цена: {prod[2]}"
        await message.answer(text_product)
        try:     #  картинки циклично повторяются
            with open(next(jpg_files), 'rb') as img:
                await message.answer_photo(img)
        except StopIteration:
            jpg_files = iter(get_file_paths_pattern('./pict', '*.jpg'))
            with open(next(jpg_files), 'rb') as img:
                await message.answer_photo(img)
    del jpg_files
    await message.answer('Выберите продукт для покупки:', reply_markup=kb_inline_buy)

@dp.message_handler(commands='start')
async def start(message):
    await message.answer('Привет! Я бот помогающий твоему здоровью.', reply_markup=kb)

@dp.message_handler(text='Рассчитать')
async def main_menu(message):
    await message.answer('Выберите опцию:', reply_markup = kb_inline)

@dp.callback_query_handler(text='product_buying')
async def send_confirm_message(call):
    await call.message.answer('Вы успешно приобрели продукт!')
    await call.answer()

@dp.callback_query_handler(text='formulas')
async def get_formulas(call):
    await call.message.answer('10 х вес (кг) + 6,25 x рост (см) – 5 х возраст (г) + 5')
    await call.answer()

@dp.callback_query_handler(text = 'calories')
async def set_age(call):
    await call.message.answer('Введите свой возраст:', reply_markup=rm)
    await call.answer()
    await UserState.age.set()

@dp.message_handler(state= UserState.age)
async def set_growth(message, state):
    await state.update_data(age = message.text)
    await message.answer('Введите свой рост:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    try:
        weight = float(message.text)
    except:
        await message.answer('При вводе веса вместо запятой используйте пожалуйста точку')
        await message.answer('Введите свой вес:')
        await UserState.weight.set()
        return
    await state.update_data(weight=message.text)
    data = await state.get_data()
    calories = 10 * float(data['weight']) + 6.25 * float(data['growth']) - 5 * float(data['age']) + 5
    await message.answer(f'Ваша норма калорий {calories}')
    await state.finish()

@dp.message_handler(text='Информация')
async def get_info_message(message):
    await message.answer('Эта кнопка выводит информацию о возможностях бота')

@dp.message_handler()
async def get_start_message(message):
    await message.answer('Введите команду /start, чтобы начать общение.')

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

