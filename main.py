import os
import re

from dotenv import load_dotenv
from pyrogram import Client, filters
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')

try:
    with open('chats.txt', 'r') as file:
        chats = file.readlines()
except FileNotFoundError:
    print('Создайте файл chats.txt и укажите в нём нужные чаты.')

username_pattern = re.compile(r'.*(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*')

chats_list = []
for chat in chats:
    chat = chat.removesuffix('\n')
    try:
        chats_list.append(int(chat))
    except ValueError:
        if bool(username_pattern.match(chat)):
            chats_list.append(chat)
print(chats_list)
try:
    with open('words.txt', 'r') as file:
        words = file.readlines()
except FileNotFoundError:
    print('Создайте файл words.txt и укажите в нём нужные слова.')

words_list = [word[:-1].strip() for word in words]
print(words_list)


async def forwarder(client: Client, message: Message):
    await message.forward('me')


app = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)

regex_handler = MessageHandler(
    forwarder, filters=filters.chat(chats=chats_list) & filters.regex(r"(?i)\b(" + '|'.join(words_list) + r")\b")
)
app.add_handler(regex_handler)

app.run()
