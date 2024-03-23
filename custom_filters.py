from pyrogram.types import Message


async def is_chats_document(_, __, m: Message):
    """
    Document name filter. Checks whether file_name equals to 'chats.txt'
    :param _:
    :param __:
    :param m:
    :return:
    """
    return m.document.file_name == 'chats.txt'
