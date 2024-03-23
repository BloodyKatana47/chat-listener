import json
import os

from dotenv import load_dotenv
from pyrogram import Client, filters, idle
from pyrogram.handlers import MessageHandler

from custom_filters import *
from files import *

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')


async def on_startup():
    """
    Sending startup message.
    :return:
    """
    await app.send_message(chat_id='me', text=f"""
🤖 Бот успешно запущен!

Доступные команды:
`/list` - показать список чатов.
    """)


async def main():
    """
    Main function for starting and stopping the bot.
    :return:
    """
    await app.start()
    await on_startup()
    await idle()
    await app.stop()


async def forwarder(client: Client, message: Message):
    """
    Forwarding all messages.
    :param client:
    :param message:
    :return:
    """
    await message.forward('me')


async def list_chats(client: Client, message: Message):
    """
    Command for sending json file with all chat IDs.
    :param client:
    :param message:
    :return:
    """
    chats = []
    async for dialog in app.get_dialogs():
        chat_id = int(dialog.chat.id)
        chat_title = dialog.chat.title
        chat_first_name = dialog.chat.first_name
        chat_last_name = dialog.chat.last_name

        if chat_title is None:
            if chat_last_name is None:
                chats.append({
                    chat_first_name: chat_id
                })
            else:
                chats.append({
                    f'{chat_first_name} {chat_last_name}': chat_id
                })
        else:
            chats.append({
                chat_title: chat_id
            })
    file_name = 'list_chats.json'
    with open(file_name, 'w') as file:
        json.dump(chats, file, indent=4, ensure_ascii=False)

    await app.send_document(
        chat_id='me', document=file_name, caption=f'''
📄 Ваш файл со всеми ID чатов, которые у вас есть.
Выберите нужные ID и отправьте их в файле chats.txt
        '''
    )
    await app.delete_messages(chat_id='me', message_ids=message.id)


async def update_chats(client: Client, message: Message):
    doc_name = message.document.file_name
    await message.download()
    new_chats = get_chats(f'downloads/{doc_name}')

    words_list = get_words('downloads/words.txt') if os.path.exists(
        os.path.join('downloads', 'words.txt')
    ) else get_words()
    new_regex_handler = MessageHandler(
        forwarder, filters=filters.chat(chats=new_chats) & filters.regex(r"(?i)\b(" + '|'.join(words_list) + r")\b")
    )
    app.remove_handler(handler=regex_handler)
    app.add_handler(new_regex_handler)
    await message.reply(text='Список чатов был успешно обновлён!', quote=True)


app = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)

regex_handler = MessageHandler(
    forwarder, filters=filters.chat(chats=get_chats()) & filters.regex(r"(?i)\b(" + '|'.join(get_words()) + r")\b")
)

command_list_handler = MessageHandler(
    list_chats, filters=filters.chat(chats='me') & filters.command(commands=['list'])
)

file_chats_filter = filters.create(is_chats_document)
file_chats_handler = MessageHandler(
    update_chats, filters=filters.chat(chats='me') & filters.document & file_chats_filter
)

app.add_handler(regex_handler)
app.add_handler(command_list_handler)
app.add_handler(file_chats_handler)

if __name__ == '__main__':
    app.run(main())
