import re
from pprint import pprint


def get_chats(file_path='chats.txt'):
    try:
        with open(file_path) as file:
            chats = file.readlines()
    except FileNotFoundError:
        print('Создайте файл chats.txt и укажите в нём нужные чаты.')
        return exit()

    username_pattern = re.compile(r'.*(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*')

    chats_list = []
    for chat in chats:
        chat = chat.removesuffix('\n')
        try:
            chats_list.append(int(chat))
        except ValueError:
            if bool(username_pattern.match(chat)):
                chats_list.append(chat)
    pprint(chats_list)
    return chats_list


def get_words(file_path='words.txt'):
    try:
        with open(file_path) as file:
            words = file.readlines()
    except FileNotFoundError:
        print('Создайте файл words.txt и укажите в нём нужные слова.')
        return exit()

    words_list = [word[:-1].strip() for word in words]
    pprint(words_list)
    return words_list
