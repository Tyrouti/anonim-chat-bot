
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from db_utils import init_db
from commands import help_command, main_menu
from handlers import choose_interest, button, connect, disconnect, leave_queue, message

def main() -> None:
    init_db()

    application = Application.builder().token("7686473429:AAFgTaGdPD8Qsm5TSFkJfOMJY_fSUtmqgSA").build()

    application.add_handler(CommandHandler("start", main_menu))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", main_menu))
    application.add_handler(CommandHandler("disconnect", disconnect))
    application.add_handler(CallbackQueryHandler(button, pattern='^interest_'))
    application.add_handler(CallbackQueryHandler(connect, pattern='^connect$'))
    application.add_handler(CallbackQueryHandler(disconnect, pattern='^disconnect$'))
    application.add_handler(CallbackQueryHandler(choose_interest, pattern='^choose_interest$'))
    application.add_handler(CallbackQueryHandler(leave_queue, pattern='^leave_queue$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    application.add_handler(MessageHandler(filters.PHOTO, message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

    application.run_polling()

if __name__ == '__main__':
    main()
