import asyncio
import schedule
import time
import service
from settings import conn,logger
from main import bot, logger

loop = asyncio.get_event_loop()

def sendMessage_sked(chat_id: str):
    frase = "Il maestro ZenDev ha parlato: " + service.getFrase()
    loop.run_until_complete(bot.send_message(chat_id=chat_id, text=frase))
    logger.info("Messaggio inviato nella chat con id %s", chat_id)
    

def startSKED():
    logger.info("SKEDULER IS RUNNING")
    resultSet = service.getAll_inInit_SKED()
    for row in resultSet:
        schedule.every().days.at(row[0]).do(sendMessage_sked,row[1]).tag('all', 'add_member', row[1])
        logger.info("Planned Skedul id %s", row[1])
    
    while True:
        schedule.run_pending()
        time.sleep(1)


def add_or_change_member_in_sked(trigger: str, chat_id: str, username: str, idUser: str):
    if(service.find_trigger_byChatid(chat_id).fetchone() != None):
        service.chage_sked(trigger=trigger, chat_id=chat_id)
        schedule.clear(chat_id)
        schedule.every().days.at(trigger).do(sendMessage_sked,chat_id).tag('all', 'changed', chat_id)
        logger.info("Modificata pianificazion la chat %s alle %s da %s (%s)", chat_id, trigger, username, idUser)
    else:
        service.save_new_sked(trigger=trigger, chat_id=chat_id)
        schedule.every().days.at(trigger).do(sendMessage_sked,chat_id).tag('all', 'add_member', chat_id)
        logger.info("Aggiunto nuovo skeduler alla pianificazione delle %s la chat con id %s da %s (%s)", trigger, chat_id, username, idUser)


def delete_sked(chat_id: str, username: str, idUser: str):
    service.delete_sked(chat_id=chat_id)
    schedule.clear(chat_id)
    logger.info("Eliminata pianificazione chat %s da %s (%s)",chat_id, username, idUser)

