startup_message: str = f"""
🤖 Бот успешно запущен!

Доступные команды:
`/list` - показать список чатов.

⚙️ Вы можете отправить сюда файлы:
`chats.txt` - для обновления списка чатов для прослушивания
`words.txt` - для обновления списка слов для прослушивания
`answers.txt` - для обновления списка заготовленных сообщений для отправки
`skip_words.txt` - для обновления списка стоп-слов
"""

spam_message: str = '**Аккаунт в спаме**'

chats_document_caption: str = f'''
📄 Ваш файл со всеми ID чатов, которые у вас есть.
Выберите нужные ID и отправьте их в файле chats.txt
'''

chats_list_updated_message: str = 'Список чатов был успешно обновлён!'

words_list_updated_message: str = 'Список слов был успешно обновлён!'

stop_words_list_updated_message: str = 'Список стоп-слов был успешно обновлён!'

answers_list_updated_message: str = 'Список заготовленных ответов был успешно обновлён!'

account_blocked_message: str = f'\n---Аккаунт заблокирован---\nУдалите из accounts.json забаненный аккаунт\n'
