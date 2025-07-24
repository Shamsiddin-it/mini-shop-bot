import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import select
from config import BOT_TOKEN
from db import Base, User, engine, async_session, Category, Product

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/add_category')], 
    [KeyboardButton(text='/cancel')], 
    [KeyboardButton(text='/show_categories')],
    [KeyboardButton(text='/add_product')]
    ], resize_keyboard=True)

class MyStates(StatesGroup):
    category_title = State()
    category_description = State()
    products = State()
    product_name = State()
    product_description = State()
    product_category = State()

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


@dp.message(F.text == '/show_categories')
async def show_categories(message: Message, state: FSMContext):
    async with async_session() as session:
        data = await session.execute(select(Category))
        print(data)
        categories = data.scalars().all()
        markup = InlineKeyboardMarkup(inline_keyboard=[])
        for i in categories:
            markup.inline_keyboard.append([InlineKeyboardButton(text=f"{i.title}", callback_data=str(i.id))])
        await message.answer("This are categories: ", reply_markup=markup)
        await state.set_state(MyStates.products)

@dp.callback_query(MyStates.products)
async def show_products(callback_query: CallbackQuery, state: FSMContext):
    # await callback_query.message.answer("These are products of category ")
    category_id = int(callback_query.data)
    async with async_session() as session:
        data = await session.execute(select(Product).filter_by(id=category_id))
        products = data.scalars().all()
        if products:
            text = [f"{j.title}--{j.description}" for j in products]
            await callback_query.message.answer(text=text)
        else:
            await callback_query.message.answer("There is no products in that category")

@dp.message(F.text == '/add_product')
async def add_product(message: Message, state: FSMContext):
    await message.answer("Write product`s name")
    await state.set_state(MyStates.product_name)
    
@dp.message(MyStates.product_name)
async def add_product_name(message: Message, state: FSMContext):
    await state.update_data(product_name=message.text)
    await message.answer("Write product`s description")
    await state.set_state(MyStates.product_description)

@dp.message(MyStates.product_description)
async def add_product_description(message: Message, state: FSMContext):
    await state.update_data(product_description=message.text)
    # await message.answer("Choose category: ")
    async with async_session() as session:
        data = await session.execute(select(Category))
        categories = data.scalars().all()
        markup = InlineKeyboardMarkup(inline_keyboard=[])
        for i in categories:
            markup.inline_keyboard.append([InlineKeyboardButton(text=f"{i.title}", callback_data=str(i.id))])
        await message.answer("Choose category below: ", reply_markup=markup)
    await state.set_state(MyStates.product_category)

@dp.callback_query(MyStates.product_category)
async def get_cagery_id_for_product(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data)
    data = await state.get_data()
    product_name = data['product_name']
    product_description = data['product_description']
    async with async_session() as session:
        session.add(Product(name = product_name, description = product_description, category_id = category_id))
        await session.commit()
    await callback.message.answer('Product added successfuly!')





async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
