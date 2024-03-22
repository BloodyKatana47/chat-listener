import os

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

with open('chats.txt', 'r') as file:
    data = file.readlines()

chats_list = [int(chat[:-1]) for chat in data]


async def forwarder(client: Client, message: Message):
    # print(type(client))
    # print(dir(client))
    # print(message.chat.id)
    # print(type(message.chat.id))
    await message.forward('me')


app = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)

regex_handler = MessageHandler(
    forwarder, filters=filters.chat(chats=chats_list) & filters.regex('^(?i)(Привет|Пока).*$')
    # forwarder, filters=filters.chat(chats=chats_list) & filters.regex('^.*(?:Привет|Пока).*$')
)
app.add_handler(regex_handler)

app.run()
