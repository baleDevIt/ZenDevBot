import logging
import sqlite3


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)
token="TOKEN"
conn = sqlite3.connect('resources.db')

welcome_message = "Ciao! Il mio nome è Zendev. Sono il saggio bot dello sviluppatore. Se stai cercando la saggezza. Non serve che chiedere!\n\n"
reply_welcome_superuser = [["Cerco Saggezza", "Voglio la saggezza per il mio canale"]]
reply_welcome_group = [["Cerco Saggezza"]]
reply_welcome_general = [["Cerco Saggezza"]]
