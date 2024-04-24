import json
import os
import random

from dotenv import load_dotenv
from pyrogram import Client, filters, idle, errors
from pyrogram.handlers import MessageHandler

from custom_filters import *
from database import Database
from files import *

load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
ADMIN_ID = os.getenv('ADMIN_ID')

db = Database('users.db')


async def on_startup():
    """
    Sends startup message.
    """
    await app.send_message(chat_id='me', text=f"""
🤖 Бот успешно запущен!

Доступные команды:
`/list` - показать список чатов.

⚙️ Вы можете отправить сюда файлы:
`chats.txt` - для обновления списка чатов для прослушивания
`words.txt` - для обновления списка слов для прослушивания
`answers.txt` - для обновления списка заготовленных сообщений для отправки
`skip_words.txt` - для обновления списка стоп-слов
    """)


async def main():
    """
    Starts and stops the bot.
    """
    await app.start()
    await on_startup()
    await idle()
    await app.stop()


async def random_answer(client: Client, message: Message):
    """
    Checks whether user exists in the database.
    In case if the one does not, it sends one random private message to the user.
    """
    if not message.from_user.is_bot:
        user_id = message.from_user.id
        user_exists = db.check_user(user_id)
        if not user_exists:
            db.create_user(user_id)

            update_answers_list = get_answers('downloads/answers.txt') if os.path.exists(
                os.path.join('downloads', 'answers.txt')
            ) else get_answers()
            random_choice = random.choice(update_answers_list)
            try:
                await app.send_message(chat_id=message.from_user.id, text=random_choice)
            except errors.UserBannedInChannel:
                await app.send_message(chat_id=int(ADMIN_ID), text='**Аккаунт в спаме!**')
                exit()


async def list_chats(client: Client, message: Message):
    """
    Sends JSON file with all chat IDs.
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
    """
    Updates chats list.
    """
    doc_name = message.document.file_name
    await message.download()
    new_chats = get_chats(f'downloads/{doc_name}')

    update_words_list = get_words('downloads/words.txt') if os.path.exists(
        os.path.join('downloads', 'words.txt')
    ) else get_words()
    new_regex_handler = MessageHandler(
        random_answer, filters=filters.chat(
            chats=new_chats
        ) & filters.regex(r"(?i)\b(" + '|'.join(update_words_list) + r")\b")
    )
    app.remove_handler(handler=regex_handler)
    app.add_handler(new_regex_handler)
    await message.reply(text='Список чатов был успешно обновлён!', quote=True)


async def update_words(client: Client, message: Message):
    """
    Updates words list.
    """
    doc_name = message.document.file_name
    await message.download()
    new_words = get_words(f'downloads/{doc_name}')

    update_chats_list = get_chats('downloads/chats.txt') if os.path.exists(
        os.path.join('downloads', 'chats.txt')
    ) else get_chats()
    new_regex_handler = MessageHandler(
        random_answer, filters=filters.chat(
            chats=update_chats_list
        ) & filters.regex(r"(?i)\b(" + '|'.join(new_words) + r")\b")
    )
    app.remove_handler(handler=regex_handler)
    app.add_handler(new_regex_handler)
    await message.reply(text='Список слов был успешно обновлён!', quote=True)


async def update_skip_words(client: Client, message: Message):
    """
    Updates skip_words list.
    """
    await message.download()
    new_skip_words = get_skip_words('downloads/skip_words.txt')

    update_chats_list = get_words('downloads/chats.txt') if os.path.exists(
        os.path.join('downloads', 'chats.txt')
    ) else get_words()
    update_words_list = get_words('downloads/words.txt') if os.path.exists(
        os.path.join('downloads', 'words.txt')
    ) else get_words()
    new_regex_handler = MessageHandler(
        random_answer, filters=filters.chat(chats=update_chats_list) & ~filters.regex(
            r"(?i)\b(" + '|'.join(new_skip_words) + r")\b"
        ) & filters.regex(
            r"(?i)\b(" + '|'.join(update_words_list) + r")\b"
        )
    )
    app.remove_handler(handler=regex_handler)
    app.add_handler(new_regex_handler)
    await message.reply(text='Список стоп-слов был успешно обновлён!', quote=True)


async def update_answers(client: Client, message: Message):
    """
    Updates answers list.
    """
    await message.download()
    await message.reply(text='Список заготовленных ответов был успешно обновлён!', quote=True)


app = Client(name="my_account", api_id=API_ID, api_hash=API_HASH)

chats_list = get_chats('downloads/chats.txt') if os.path.exists(
    os.path.join('downloads', 'chats.txt')
) else get_chats()
words_list = get_words('downloads/words.txt') if os.path.exists(
    os.path.join('downloads', 'words.txt')
) else get_words()
skip_words_list = get_skip_words('downloads/skip_words.txt') if os.path.exists(
    os.path.join('downloads', 'skip_words.txt')
) else get_skip_words()

if len(skip_words_list) == 0:
    regex_handler = MessageHandler(
        random_answer,
        filters=filters.chat(chats=chats_list) & filters.regex(r"(?i)\b(" + '|'.join(words_list) + r")\b")
    )
else:
    regex_handler = MessageHandler(
        random_answer,
        filters=filters.chat(chats=chats_list) & ~filters.regex(
            r"(?i)\b(" + '|'.join(skip_words_list) + r")\b"
        ) & filters.regex(
            r"(?i)\b(" + '|'.join(words_list) + r")\b"
        )
    )

command_list_handler = MessageHandler(
    list_chats, filters=filters.chat(chats='me') & filters.command(commands=['list'])
)

file_chats_filter = filters.create(is_chats_document)
file_chats_handler = MessageHandler(
    update_chats, filters=filters.chat(chats='me') & filters.document & file_chats_filter
)

file_words_filter = filters.create(is_words_document)
file_words_handler = MessageHandler(
    update_words, filters=filters.chat(chats='me') & filters.document & file_words_filter
)

file_skip_words_filter = filters.create(is_skip_words_document)
file_skip_words_handler = MessageHandler(
    update_skip_words, filters=filters.chat(chats='me') & filters.document & file_skip_words_filter
)

file_answers_filter = filters.create(is_answers_document)
file_answers_handler = MessageHandler(
    update_answers, filters=filters.chat(chats='me') & filters.document & file_answers_filter
)

app.add_handler(regex_handler)
app.add_handler(command_list_handler)
app.add_handler(file_chats_handler)
app.add_handler(file_words_handler)
app.add_handler(file_skip_words_handler)
app.add_handler(file_answers_handler)

if __name__ == '__main__':
    try:
        app.run(main())
    except errors.PhoneNumberBanned:
        print(f'\n---Аккаунт заблокирован---\n')
        exit()
