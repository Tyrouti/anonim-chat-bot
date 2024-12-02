import sqlite3
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from commands import main_menu
from db_utils import get_partner, set_partner, set_interest, get_interest, set_in_queue


async def choose_interest(update: Update) -> None:
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Искусство", callback_data='interest_art')],
        [InlineKeyboardButton("Технологии", callback_data='interest_tech')],
        [InlineKeyboardButton("Спорт", callback_data='interest_sport')],
        [InlineKeyboardButton("Музыка", callback_data='interest_music')],
        [InlineKeyboardButton("Кино", callback_data='interest_movies')],
        [InlineKeyboardButton("Путешествия", callback_data='interest_travel')],
        [InlineKeyboardButton("Назад в меню", callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Выберите ваш интерес:", reply_markup=reply_markup)

async def button(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data.startswith('interest_'):
        interest = query.data.split('_')[1]
        user_id = query.from_user.id
        set_interest(user_id, interest)
        await main_menu(update)

    elif query.data == 'main_menu':
        await main_menu(update)


async def connect(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id
    user_interest = get_interest(user_id)

    if get_partner(user_id) is not None:
        await query.edit_message_text('Вы уже подключены к собеседнику.')
        return

    set_in_queue(user_id, 1)

    keyboard = [
        [InlineKeyboardButton("Отменить поиск", callback_data='leave_queue')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text('Ищем собеседника...', reply_markup=reply_markup)

    conn = sqlite3.connect('chat_bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE partner_id IS NULL AND id != ? AND interest = ? AND in_queue = 1', (user_id, user_interest))
    result = cursor.fetchone()

    if result:
        partner_id = result[0]
        set_partner(user_id, partner_id)
        set_partner(partner_id, user_id)
        set_in_queue(user_id, 0)
        set_in_queue(partner_id, 0)
        await context.bot.send_message(partner_id, 'Вы подключены к новому собеседнику!')
        await query.edit_message_text('Вы подключены к новому собеседнику!')
    else:
        set_in_queue(user_id, 1)

    conn.close()


async def disconnect(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.callback_query:
        query = update.callback_query
        user_id = query.from_user.id
        user_first_name = query.from_user.first_name
    else:
        query = None
        user_id = update.effective_user.id
        user_first_name = update.effective_user.first_name

    partner_id = get_partner(user_id)

    if partner_id is None:
        if query:
            await query.answer('Вы не подключены к собеседнику.')
        else:
            await update.message.reply_text('Вы не подключены к собеседнику.')
        return

    set_partner(partner_id, None)
    set_partner(user_id, None)

    if query:
        await query.answer('Вы отключились от собеседника.')
        await query.message.reply_text('Возвращаем вас в главное меню...')
    else:
        await update.message.reply_text('Вы отключились от собеседника. Возвращаем вас в главное меню...')

    await context.bot.send_message(partner_id, f'Ваш собеседник отключился. Возвращаем вас в главное меню...')

    await main_menu(update)

    fake_update = Update.de_json({
        'update_id': 0,
        'message': {
            'message_id': 0,
            'chat': {'id': partner_id, 'type': 'private'},
            'from': {'id': partner_id, 'is_bot': False, 'first_name': user_first_name},
            'date': datetime.now().timestamp(),
            'text': '/start'
        }
    }, context.bot)

    await main_menu(fake_update)


async def message(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    partner_id = get_partner(user_id)

    if partner_id is None:
        await update.message.reply_text('Вы еще не подключены к собеседнику. Используйте /start для начала.')
        return

    if update.message.text:
        await context.bot.send_message(partner_id, update.message.text)
    elif update.message.photo:
        photo = update.message.photo[-1]
        await context.bot.send_photo(partner_id, photo.file_id, caption=update.message.caption)

async def leave_queue(update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user_id = query.from_user.id

    set_in_queue(user_id, 0)
    await query.edit_message_text('Вы покинули очередь.')
    await context.bot.send_message(user_id, 'Вы успешно вышли из очереди поиска.')
    await main_menu(update)

