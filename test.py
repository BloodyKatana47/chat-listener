with open('chats.txt', 'r') as file:
    data = file.readlines()
x = [int(chat[:-1]) for chat in data]
print(x)
