#!/usr/bin/env python

import multiprocessing
import skeduler
import service
import settings
from settings import logger, conn
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 5):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

bot = Bot(token=settings.token)
STEP1, STEP2, FORWORD_MESSAGGIO, settings_SKED, CHANGE_SKED, EXIT = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    logger.info("Start chat - %s (%i) - CHATID(%i)  ", update.message.from_user.username, update.message.from_user.id, update.message.chat_id)
    if(update.message.chat.type == 'supergroup'):
        reply_keyboard = settings.reply_welcome_superuser
    elif(update.message.chat.type == 'group'):
        reply_keyboard = settings.reply_welcome_group
    else:
        reply_keyboard = settings.reply_welcome_general

    await update.message.reply_text( 
        settings.welcome_message,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Cosa vuoi veramente?"
        ),
    )
    return STEP1       


async def cerco_saggezza(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Start chat - %s (%i) - CHATID(%i)  ", update.message.from_user.username, update.message.from_user.id, update.message.chat_id)
    frase = "IL MAESTRO DICE... \n\n" + service.getFrase()    
    await update.message.reply_text(
        frase,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def saggezza_canale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Cerco la saggezza %s %s: ChatId: %i", user.first_name, user.last_name, update.message.chat_id)
    reply_keyboard = [["09:00", "12:00","14:00","18:00"]]


    if(update.message.chat.type == 'supergroup'):
        resultSet = service.find_trigger_byChatid(update.message.chat_id)
        if(resultSet.fetchone() != None):
            reply_keyboard = [["Modifica", "Elimina", "Back"]]
            await update.message.reply_text(
                "E' già presente una pianificazione per questo canale, vuoi modificarla?",
                reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Vuoi modificarla?"
            ))
            return STEP2
        
        print("sono qui!")
        await update.message.reply_text(
                "A che ora vuoi che porti la saggezza su questo canale?",
                reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Scegli esclusivamente uno di questi orari..."
            ))
        return settings_SKED
    else:
        await update.message.reply_text(
            "Devi rendermi un amministatore se vuoi che porti la saggezza",
            reply_markup=ReplyKeyboardRemove()
        )
        return EXIT

async def setTrigger_sked_in_modify(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["09:00", "12:00","14:00","18:00"]]
    for row in service.find_trigger_byChatid(chat_id=update.message.chat.id):
        trigger = row[0]
        break
    await update.message.reply_text(
                "Attualmente porto la saggezza sul gruppo alle {TRIGGER} \n A che ora vuoi che porti la saggezza su questo canale?".format(TRIGGER=trigger),
                reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Scegli esclusivamente uno di questi orari..."
            ))
    return settings_SKED
    

async def settings_sked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    skeduler.add_or_change_member_in_sked(update.message.text,update.message.chat.id, update.message.from_user.username, update.message.from_user.id)
    await update.message.reply_text(
        "Ho impostato il tutto, riceverai la mia saggezza ogni giorno all'ora prestabilita", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


async def delete_sked(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    skeduler.delete_sked(update.message.chat.id, update.message.from_user.username, update.message.from_user.id)
    await update.message.reply_text(
        "Ho eliminato la pianificazione per questo gruppo!", reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END




async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s %s with chatid %i canceled the conversation.", user.first_name, user.last_name, update.message.chat_id)
    await update.message.reply_text(
        "Che la saggezza sia con te!.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END



def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(settings.token).build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("zen", start)],
        states={
            STEP1: [MessageHandler(filters.Regex("^(Cerco Saggezza)$"), cerco_saggezza), 
                    MessageHandler(filters.Regex("^(Voglio la saggezza per il mio canale)$"), saggezza_canale)],
            STEP2: [MessageHandler(filters.Regex("^(Modifica)$"), setTrigger_sked_in_modify),
                    MessageHandler(filters.Regex("^(Elimina)$"), delete_sked), 
                    MessageHandler(filters.Regex("^(Back)$"), start)],
            settings_SKED: [MessageHandler(filters.Regex("^(09:00|12:00|14:00|18:00)$"), settings_sked)],
        },
        fallbacks=[CommandHandler("exit", cancel)],
    )
    application.add_handler(conv_handler)
    # Run the bot until the user presses Ctrl-C

    multiprocessing.Process(target=skeduler.startSKED).start()
    application.run_polling()



if __name__ == "__main__":
    main()