import json
import os
import random
from typing import List, Union, Dict, Tuple

from lingua import Language, LanguageDetectorBuilder, LanguageDetector
from pyrogram import Client, filters, idle, errors
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message

from core import settings, load_accounts_configs
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

ADMIN_USERNAME: str = settings.admin_username
DATABASE_NAME: str = settings.database_name
FILE_FOLDER_NAME: str = settings.files_folder_name
SESSION_FOLDER_NAME: str = settings.sessions_folder_name

db: Database = Database(DATABASE_NAME)
active_handler: List[MessageHandler] = []

apps: List[Client] = [
    Client(
        name=value['session_name'],
        api_id=value['api_id'],
        api_hash=value['api_hash'],
        workdir=SESSION_FOLDER_NAME
    ).start() for value in load_accounts_configs()
]

app: Client = apps[0]


def update_handler(chats: List[str], words: List[str]) -> None:
    """
    Takes a list of chats and a list of words, removes old handler and registers a new one.
    """
    updated_handler: MessageHandler = MessageHandler(
        random_answer, filters=filters.chat(
            chats=chats
        ) & filters.regex(r"(?i)\b(" + '|'.join(words) + r")\b")
    )

    app.remove_handler(handler=active_handler[0])
    active_handler.pop(0)

    active_handler.append(updated_handler)
    app.add_handler(updated_handler)


async def on_startup() -> None:
    """
    Sends startup message.
    """
    try:
        os.mkdir(FILE_FOLDER_NAME)
    except FileExistsError:
        pass

    try:
        os.mkdir(SESSION_FOLDER_NAME)
    except FileExistsError:
        pass

    await app.send_message(chat_id='me', text=startup_message)


async def main() -> None:
    """
    Calls startup() function for sending startup message and stops
    """
    await on_startup()
    await idle()
    for _app in apps:
        await _app.stop()


async def random_answer(client: Client, message: Message) -> None:
    """
    Checks whether user exists in the database.
    In case if the one does not, it sends one random private message to the user.
    """
    if message.from_user is not None and not message.from_user.is_bot:
        user_id: int = message.from_user.id
        user_exists: bool = db.check_user(user_id)
        if not user_exists:
            message_text_and_caption: Tuple[Union[str, None], Union[str, None]] = message.text, message.caption
            message_content: str = next(filter(lambda text: text is not None, message_text_and_caption), None)

            languages: List[Language] = [Language.RUSSIAN, Language.UKRAINIAN, Language.ENGLISH]
            detector: LanguageDetector = LanguageDetectorBuilder.from_languages(*languages).build()
            content_language: Language = detector.detect_language_of(message_content)
            content_language_short_name: str = content_language.iso_code_639_1.name.lower()

            file_name: str = f'answers_{content_language_short_name}.txt'
            file_exists: bool = os.path.exists(os.path.join(FILE_FOLDER_NAME, file_name))
            update_answers_list: List[str] = get_answers(
                f'{FILE_FOLDER_NAME}/{file_name}'
            ) if file_exists else get_answers()
            random_choice: str = random.choice(update_answers_list)

            for account in apps:
                api_hash: str = account.api_hash
                availability: Union[Tuple[int], None] = db.check_availability(api_hash=api_hash)
                try:
                    await account.send_message(chat_id=message.from_user.id, text=random_choice)

                    if availability is None:
                        db.save_account(api_hash=api_hash)
                    else:
                        db.update_availability(api_hash=api_hash, availability=1)

                    db.save_user(user_id)
                    break
                except errors.UserBannedInChannel:
                    if availability is None:
                        db.save_account(api_hash=api_hash)
                        db.update_availability(api_hash=api_hash, availability=0)

                        await account.send_message(chat_id=ADMIN_USERNAME, text=spam_message)
                    elif availability[0] == 1:
                        db.update_availability(api_hash=api_hash, availability=0)

                        await account.send_message(chat_id=ADMIN_USERNAME, text=spam_message)
                    else:
                        continue


async def list_chats(client: Client, message: Message) -> None:
    """
    Sends JSON file with all chat IDs.
    """
    chats: List[Dict[str, int]] = []
    async for dialog in app.get_dialogs():
        chat_id: int = int(dialog.chat.id)
        chat_title: Union[str, None] = dialog.chat.title
        chat_first_name: str = dialog.chat.first_name
        chat_last_name: Union[str, None] = dialog.chat.last_name

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
    file_name: str = 'list_chats.json'
    with open(file_name, 'w') as file:
        json.dump(chats, file, indent=4, ensure_ascii=False)

    await app.send_document(chat_id='me', document=file_name, caption=chats_document_caption)
    await app.delete_messages(chat_id='me', message_ids=message.id)


async def update_words(client: Client, message: Message) -> None:
    """
    Updates words list.
    """
    await message.download()
    load_chats: List[Union[str, int]] = get_chats(f'{FILE_FOLDER_NAME}/chats.txt')
    load_words: List[str] = get_words(f'{FILE_FOLDER_NAME}/words.txt') if os.path.exists(
        os.path.join(FILE_FOLDER_NAME, 'words.txt')
    ) else get_words()

    update_handler(words=load_words, chats=load_chats)

    await message.reply(text=words_list_updated_message, quote=True)


async def update_chats(client: Client, message: Message) -> None:
    """
    Updates chats list.
    """
    await message.download()
    load_words: List[str] = get_words(f'{FILE_FOLDER_NAME}/words.txt')
    load_chats: List[Union[str, int]] = get_chats(f'{FILE_FOLDER_NAME}/chats.txt') if os.path.exists(
        os.path.join(FILE_FOLDER_NAME, 'chats.txt')
    ) else get_chats()

    update_handler(words=load_words, chats=load_chats)

    await message.reply(text=chats_list_updated_message, quote=True)


async def update_skip_words(client: Client, message: Message) -> None:
    """
    Updates skip_words list.
    """
    await message.download()
    load_skip_words: List[str] = get_skip_words(f'{FILE_FOLDER_NAME}/skip_words.txt')
    load_chats: List[str] = get_words(f'{FILE_FOLDER_NAME}/chats.txt') if os.path.exists(
        os.path.join(FILE_FOLDER_NAME, 'chats.txt')
    ) else get_words()
    load_words: List[str] = get_words(f'{FILE_FOLDER_NAME}/words.txt') if os.path.exists(
        os.path.join(FILE_FOLDER_NAME, 'words.txt')
    ) else get_words()

    updated_handler: MessageHandler = MessageHandler(
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


async def update_answers(client: Client, message: Message) -> None:
    """
    Updates answers list.
    """
    await message.download()
    await message.reply(text=answers_list_updated_message, quote=True)


chats_list: List[Union[str, int]] = get_chats(f'{FILE_FOLDER_NAME}/chats.txt') if os.path.exists(
    os.path.join(FILE_FOLDER_NAME, 'chats.txt')
) else get_chats()
words_list: List[str] = get_words(f'{FILE_FOLDER_NAME}/words.txt') if os.path.exists(
    os.path.join(FILE_FOLDER_NAME, 'words.txt')
) else get_words()
skip_words_list: List[str] = get_skip_words(f'{FILE_FOLDER_NAME}/skip_words.txt') if os.path.exists(
    os.path.join(FILE_FOLDER_NAME, 'skip_words.txt')
) else get_skip_words()


def _return_main_handlers(handler: str):
    """
    Returns handlers for all documents.
    """
    if handler == 'chats':
        return MessageHandler(
            update_chats,
            filters=filters.chat('me') & filters.document & filters.create(is_chats_document)
        )
    elif handler == 'words':
        return MessageHandler(
            update_words,
            filters=filters.chat(chats='me') & filters.document & filters.create(is_words_document)
        )
    elif handler == 'skip_words':
        return MessageHandler(
            update_skip_words,
            filters=filters.chat(chats='me') & filters.document & filters.create(is_skip_words_document)
        )
    elif handler == 'answers':
        return MessageHandler(
            update_answers,
            filters=filters.chat(chats='me') & filters.document & filters.create(is_answers_document)
        )
    elif handler == 'list':
        return MessageHandler(
            list_chats,
            filters=filters.chat(chats='me') & filters.command(commands=['list'])
        )
    else:
        if len(skip_words_list) == 0:
            return MessageHandler(
                random_answer,
                filters=filters.chat(chats=chats_list) & filters.regex(r"(?i)\b(" + '|'.join(words_list) + r")\b")
            )
        else:
            return MessageHandler(
                random_answer,
                filters=filters.chat(chats=chats_list) & ~filters.regex(
                    r"(?i)\b(" + '|'.join(skip_words_list) + r")\b"
                ) & filters.regex(
                    r"(?i)\b(" + '|'.join(words_list) + r")\b"
                )
            )


for handler_type in ['main', 'list', 'words', 'chats', 'skip_words', 'answers']:
    if handler_type == 'main':
        active_handler.append(_return_main_handlers(handler_type))
    app.add_handler(_return_main_handlers(handler_type))

if __name__ == '__main__':
    try:
        app.run(main())
    except errors.PhoneNumberBanned:
        print(account_blocked_message)
        exit()
