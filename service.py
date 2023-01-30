import sqlite3
import random

conn = sqlite3.connect('resources.db')


def getFrase() -> str:
    limit = conn.execute("SELECT COUNT(*) FROM FRASE").fetchall()
    cursor = conn.execute("SELECT PHARSE from FRASE where id={id}".format(id=random.randint(0,limit[-1][-1])))
    for row in cursor:
        return row[0]
    
def find_trigger_byChatid(chat_id: str):
    return conn.execute("SELECT TRIGGER, CHATID FROM SKED WHERE CHATID='{CHATID}'".format(CHATID= chat_id))

def save_new_sked(trigger: str, chat_id: str):
    conn.execute("INSERT INTO SKED (TRIGGER, CHATID) VALUES('{TRIGGER}','{CHATID}');".format(TRIGGER = trigger , CHATID= chat_id))
    conn.commit()
    return

def chage_sked(trigger: str, chat_id: str):
    print("UPDATE SKED SET TRIGGER='{TRIGGER}' WHERE CHATID='{CHATID}';".format(TRIGGER = trigger , CHATID= chat_id))
    conn.execute("UPDATE SKED SET TRIGGER='{TRIGGER}' WHERE CHATID='{CHATID}';".format(TRIGGER = trigger , CHATID= chat_id))
    conn.commit()
    return

def delete_sked(chat_id: str):
    conn.execute("DELETE FROM SKED WHERE CHATID='{CHATID}';".format(CHATID= chat_id))
    conn.commit()
    return

def getAll_inInit_SKED():
    return conn.execute("SELECT TRIGGER, CHATID FROM SKED")