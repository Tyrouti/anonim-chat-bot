from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from db_utils import get_in_queue


async def help_command(update) -> None:
    commands = """
    /start - Начать или вернуться в главное меню
    /help - Показать список команд
    /menu - Вернуться в главное меню
    /disconnect - Отключиться от собеседника
    """
    await update.message.reply_text(commands)

async def main_menu(update) -> None:
    user = update.effective_user
    in_queue = get_in_queue(user.id)
    keyboard = [
        [InlineKeyboardButton("Начать поиск собеседника", callback_data='connect')],
        [InlineKeyboardButton("Отключиться", callback_data='disconnect')]
    ]
    if in_queue == 0:
        keyboard.insert(0, [InlineKeyboardButton("Выбрать интерес", callback_data='choose_interest')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_html(
            rf'Привет, {user.mention_html()}! Добро пожаловать в анонимный чат бот.',
            reply_markup=reply_markup,
        )
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(
            text=rf'Привет, {user.mention_html()}! Добро пожаловать в анонимный чат бот.',
            reply_markup=reply_markup,
        )
