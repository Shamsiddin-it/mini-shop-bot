import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from config import BOT_TOKEN
from db import Base, User, engine, async_session, Category

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/add_category')], [KeyboardButton(text='/cancel')]], resize_keyboard=True)

class MyStates(StatesGroup):
    category_title = State()
    category_description = State()

@dp.message(F.text == '/start')
async def start(message: Message):
    await message.answer("Welcome to our mini shop bot!", reply_markup=kb)
    async with async_session() as session:
        user = User(username=message.from_user.username, tg_id=message.from_user.id)
        user1 = await session.scalar(select(User).filter_by(tg_id=message.from_user.id))
        if not user1:
            session.add(user)
            await session.commit()

@dp.message(F.text == '/add_category')
async def add_category(message: Message, state: FSMContext):
    await message.answer("Write category title: ")
    await state.set_state(MyStates.category_title)

@dp.message(MyStates.category_title)
async def get_category_title(message: Message, state: FSMContext):
    category_title = message.text
    await state.update_data(category_title=category_title)
    await message.answer("Write category description: ")
    await state.set_state(MyStates.category_description)

@dp.message(MyStates.category_description)
async def get_category_description_add_category(message: Message, state: FSMContext):
    category_description = message.text
    data = await state.get_data()
    category_title = data['category_title']
    async with async_session() as session:
        category = await session.scalar(select(Category).filter_by(title=category_title))
        if not category:
            session.add(Category(title=category_title, description=category_description))
            await session.commit()
            await message.answer('Category added successfuly!')
        else:
            await message.answer("Category already exists!")

@dp.message(F.text == '/cancel')
async def cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Operation cancelled!")

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
