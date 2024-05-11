from re import compile, Pattern
from pprint import pprint
from typing import Union, List


def get_chats(file_path: str = 'chats.txt') -> Union[List[Union[str, int]], exit]:
    """
    Opens file 'chats.txt' and returns a list of chats.
    """
    try:
        with open(file_path, encoding='utf-8') as file:
            chats: List[str] = [line.strip() for line in file if line.strip()]
        if len(chats) == 0:
            raise ValueError
    except FileNotFoundError:
        print('Создайте файл chats.txt и укажите в нём нужные чаты.')
        return exit()
    except ValueError:
        print('Заполните файл chats.txt нужными чатами.')
        return exit()

    username_pattern: Pattern = compile(r'.*(?=\w{5,32}\b)[a-zA-Z0-9]+(?:_[a-zA-Z0-9]+)*.*')

    chats_list: List[Union[int, str]] = []
    for chat in chats:
        try:
            chats_list.append(int(chat))
        except ValueError:
            if bool(username_pattern.match(chat)):
                chats_list.append(chat)
    pprint(chats_list)
    return chats_list


def get_words(file_path: str = 'words.txt') -> Union[List[str], exit]:
    """
    Opens 'words.txt' and returns a list of words.
    """
    try:
        with open(file_path, encoding='utf-8') as file:
            words_list: List[str] = [line.strip() for line in file if line.strip()]
        if len(words_list) == 0:
            raise ValueError
    except FileNotFoundError:
        print('Создайте файл words.txt и укажите в нём нужные слова.')
        return exit()
    except ValueError:
        print('Заполните файл words.txt нужными словами.')
        return exit()
    pprint(words_list)
    return words_list


def get_skip_words(file_path: str = 'skip_words.txt') -> Union[List[str], exit]:
    """
    Opens 'skip_words.txt' and returns a list of skip-words.
    """
    try:
        with open(file_path, encoding='utf-8') as file:
            skip_words_list: List[str] = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return []
    pprint(skip_words_list)
    return skip_words_list


def get_answers(file_path: str = 'answers.txt') -> Union[List[str], exit]:
    """
    Opens 'answers.txt' and returns a list of answers.
    """
    try:
        with open(file_path, encoding='utf-8') as file:
            answers: List[str] = file.read().split('===')
        if answers[0] == '':
            raise ValueError
    except FileNotFoundError:
        print('Создайте файл answers.txt и укажите в нём нужные заготовленные ответы.')
        return exit()
    except ValueError:
        print('Заполните файл answers.txt нужными ответами.')
        return exit()
    return answers
