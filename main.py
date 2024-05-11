import json
import os
import random
from typing import List, Union

from pyrogram import Client, filters, idle, errors
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from core import settings
from database import Database
from filters import is_chats_document, is_words_document, is_skip_words_document, is_answers_document
from utils.captions import (
    startup_message,
    spam_message,
    chats_document_caption,
    chats_list_updated_message,
    words_list_updated_message,
    stop_words_list_updated_message,
    answers_list_updated_message,
    account_blocked_message,
)
from utils.files import get_chats, get_words, get_skip_words, get_answers

API_ID = settings.api_id
API_HASH = settings.api_hash
ADMIN_ID = settings.admin_id
DATABASE_NAME = settings.database_name
SESSION_NAME = settings.session_name
FOLDER_NAME = settings.folder_name

db = Database(DATABASE_NAME)
active_handler = []


async def on_startup():
    """
    Sends startup message.
    """
    await app.send_message(chat_id='me', text=startup_message)


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
    if message.from_user is not None and not message.from_user.is_bot:
        user_id = message.from_user.id
        user_exists = db.check_user(user_id)
        if not user_exists:
            db.create_user(user_id)

            update_answers_list = get_answers(f'{FOLDER_NAME}/answers.txt') if os.path.exists(
                os.path.join(FOLDER_NAME, 'answers.txt')
            ) else get_answers()
            random_choice = random.choice(update_answers_list)
            try:
                await app.send_message(chat_id=message.from_user.id, text=random_choice)
            except errors.UserBannedInChannel:
                await app.send_message(chat_id=ADMIN_ID, text=spam_message)
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

    await app.send_document(chat_id='me', document=file_name, caption=chats_document_caption)
    await app.delete_messages(chat_id='me', message_ids=message.id)


async def update_words(client: Client, message: Message):
    """
    Updates words list.
    """
    await message.download()
    load_chats = get_chats(f'{FOLDER_NAME}/chats.txt')
    load_words = get_words(f'{FOLDER_NAME}/words.txt') if os.path.exists(
        os.path.join(FOLDER_NAME, 'words.txt')
    ) else get_words()

    updated_handler = MessageHandler(
        random_answer, filters=filters.chat(
            chats=load_chats
        ) & filters.regex(r"(?i)\b(" + '|'.join(load_words) + r")\b")
    )

    app.remove_handler(handler=active_handler[0])
    active_handler.pop(0)

    active_handler.append(updated_handler)
    app.add_handler(updated_handler)

    await message.reply(text=words_list_updated_message, quote=True)


async def update_chats(client: Client, message: Message):
    """
    Updates chats list.
    """
    await message.download()
    load_words = get_words(f'{FOLDER_NAME}/words.txt')
    load_chats = get_chats(f'{FOLDER_NAME}/chats.txt') if os.path.exists(
        os.path.join(FOLDER_NAME, 'chats.txt')
    ) else get_chats()

    updated_handler = MessageHandler(
        random_answer, filters=filters.chat(
            chats=load_chats
        ) & filters.regex(r"(?i)\b(" + '|'.join(load_words) + r")\b")
    )

    app.remove_handler(handler=active_handler[0])
    active_handler.pop(0)

    active_handler.append(updated_handler)
    app.add_handler(updated_handler)

    await message.reply(text=chats_list_updated_message, quote=True)


async def update_skip_words(client: Client, message: Message):
    """
    Updates skip_words list.
    """
    await message.download()
    load_skip_words = get_skip_words(f'{FOLDER_NAME}/skip_words.txt')
    load_chats = get_words(f'{FOLDER_NAME}/chats.txt') if os.path.exists(
        os.path.join(FOLDER_NAME, 'chats.txt')
    ) else get_words()
    load_words = get_words(f'{FOLDER_NAME}/words.txt') if os.path.exists(
        os.path.join(FOLDER_NAME, 'words.txt')
    ) else get_words()

    updated_handler = MessageHandler(
        random_answer, filters=filters.chat(chats=load_chats) & ~filters.regex(
            r"(?i)\b(" + '|'.join(load_skip_words) + r")\b"
        ) & filters.regex(
            r"(?i)\b(" + '|'.join(load_words) + r")\b"
        )
    )

    app.remove_handler(handler=active_handler[0])
    active_handler.pop(0)

    active_handler.append(updated_handler)
    app.add_handler(updated_handler)

    await message.reply(text=stop_words_list_updated_message, quote=True)


async def update_answers(client: Client, message: Message):
    """
    Updates answers list.
    """
    await message.download()
    await message.reply(text=answers_list_updated_message, quote=True)


app = Client(name=SESSION_NAME, api_id=API_ID, api_hash=API_HASH)

chats_list = get_chats(f'{FOLDER_NAME}/chats.txt') if os.path.exists(
    os.path.join(FOLDER_NAME, 'chats.txt')
) else get_chats()
words_list = get_words(f'{FOLDER_NAME}/words.txt') if os.path.exists(
    os.path.join(FOLDER_NAME, 'words.txt')
) else get_words()
skip_words_list = get_skip_words(f'{FOLDER_NAME}/skip_words.txt') if os.path.exists(
    os.path.join(FOLDER_NAME, 'skip_words.txt')
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

active_handler.append(regex_handler)
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
        print(account_blocked_message)
        exit()
