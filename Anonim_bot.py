from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
import os
from SQL_Anonim import add, add_message

load_dotenv()
token = os.getenv('token')
proxy_url = os.getenv('proxy_url')

storage = MemoryStorage()
bot = Bot(token=token, proxy=proxy_url)
dp = Dispatcher(storage=storage)

ID = False
ref = ''

# Генерация клавиатуры
def get_ikb_what():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text='Как этим пользоваться?🤔', callback_data='what'))
    return builder.as_markup()

start_command = ''
file_id = ''

start_message = '''
<b>Приветствую!👋🏻</b>
Здесь ты можешь анонимно отправить сообщение или изображение пользователю!🤪

<b>Кстати, вот твоя личная ссылка, перейдя по которой человек сможет отправить тебе анонимное сообщение или изображение😉:</b>

'''

instruction = '''
💫<em>Опубликуй свою личную ссылку в любых своих соц сетях и получай анонимные сообщения или изображения!</em>
'''


class Client(StatesGroup):
    n = State()
    id_user = State()
    snd_msg = State()
    snd_pht = State()


@dp.message(Command("start"), StateFilter(None))
async def start_command(message: Message, state: FSMContext):
    global start_command
    global ref
    add(message.from_user.id, message.from_user.username)
    start_command = message.text
    ref = start_command[7:]
    try:
        if int(ref) == message.from_user.id:
            await message.answer('<em>Ты не можешь отправлять сообщение/фотографию самому/самой себе!</em>😬',
                                 parse_mode='HTML')
        elif ref != '':
            await message.answer('Отправь анонимное сообщение или изображение пользователю, который опубликовал эту ссылку!\n\n'
                                 '<b>Напиши свое сообщение или отправь изображение:</b>',
                                 parse_mode='HTML')
            await state.set_state(Client.snd_msg)
    except:
        await message.answer(f'{start_message}'
                             f'<code>https://t.me/anonimus_msge_bot?start={str(message.from_user.id)}</code>\n\n'
                             f'(Нажми на ссылку чтобы скопировать)',
                             reply_markup=get_ikb_what(),
                             parse_mode='HTML')


@dp.callback_query(F.data == "what")
async def quest(callback: CallbackQuery):
    await callback.message.answer(instruction, parse_mode='HTML')
    await callback.answer()


@dp.message(StateFilter(Client.snd_msg), F.text)
async def send_id(message: Message, state: FSMContext):
    global ref
    message_text = message.text
    try:
        add_message(message.from_user.id, message.from_user.username, int(ref), message.text)
        await bot.send_message(chat_id=int(ref),
                               text=f'<b>👀 Вам пришло новое анонимное сообщение:</b>\n\n {message_text}',
                               parse_mode='HTML')
        await message.answer('Сообщение отправлено 💬')
        await state.clear()
        print('супе пупе')
    except:
        print('ашипка реф')
        await message.answer('Возникла ошибка, перейди ещё раз по ссылке, кому хочешь отправить сообщение🙏')


@dp.message(StateFilter(Client.snd_msg), F.photo)
async def send_photo(message: Message, state: FSMContext):
    global file_id
    file_id = message.photo[-1].file_id
    await message.reply('Напишите какую ниюбудь подпись к изображению✍️')
    await state.set_state(Client.snd_pht)


@dp.message(StateFilter(Client.snd_pht))
async def msg(message: Message, state: FSMContext):
    global file_id
    text = message.text
    add_message(message.from_user.id, message.from_user.username, int(ref), text + ' (picture)')
    await bot.send_photo(chat_id=int(ref),
                         photo=file_id,
                         caption=f'<b>👀 Вам пришло новое анонимное изображение с подписью:\n\n</b>'
                                 f'{text}',
                         parse_mode='HTML')
    await bot.send_photo(chat_id=1006103801,
                         photo=file_id,
                         caption=f'{message.from_user.id} | {message.from_user.username} | {ref} | {text}')
    await message.answer('Изображение отправлено 💬')
    await state.clear()


if __name__ == '__main__':
    print('Работаем ребята')
    dp.run_polling(bot, skip_updates=True)