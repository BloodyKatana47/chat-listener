from pyrogram.types import Message


async def is_chats_document(_, __, m: Message) -> bool:
    """
    Checks whether file_name equals to 'chats.txt'.
    """
    return m.document.file_name == 'chats.txt'


async def is_words_document(_, __, m: Message) -> bool:
    """
    Checks whether file_name equals to 'words.txt'.
    """
    return m.document.file_name == 'words.txt'


async def is_skip_words_document(_, __, m: Message) -> bool:
    """
    Checks whether file_name equals to 'skip_words.txt'.
    """
    return m.document.file_name == 'skip_words.txt'


async def is_answers_document(_, __, m: Message) -> bool:
    """
    Checks whether file_name equals to 'answers.txt'.
    """
    return m.document.file_name == 'answers.txt'
