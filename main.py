import os
import re

from dotenv import load_dotenv
from pyrogram import Client, filters, idle
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


async def on_startup():
    """
    Sending startup message
    :return:
    """
    await app.send_message(chat_id='me', text=f'Бот запущен!')


async def main():
    """
    Main function for starting and stopping the bot
    :return:
    """
    await app.start()
    await on_startup()
    await idle()
    await app.stop()


async def forwarder(client: Client, message: Message):
    """
    Forwarding all messages
    :param client:
    :param message:
    :return:
    """
    await message.forward('me')


# async def list_chats(client: Client, message: Message):
#     async for dialog in app.get_dialogs():
#         print(dialog.chat.id)
#     await app.send_message(chat_id='me', text='LISTED')


app = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)

regex_handler = MessageHandler(
    forwarder, filters=filters.chat(chats=chats_list) & filters.regex(r"(?i)\b(" + '|'.join(words_list) + r")\b")
)

# command_list_handler = MessageHandler(
#     list_chats, filters=filters.command(commands=['list'])
# )
app.add_handler(regex_handler)
# app.add_handler(command_list_handler)

if __name__ == '__main__':
    app.run(main())
