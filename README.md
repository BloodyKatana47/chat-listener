# 🤖 Chat Listener

### The user bot based on Pyrogram allows to track specific words in listed chats and send one random message to the user whose message contains one of the desired words

### The bot can be useful for marketing purposes

<div align="center">
<img alt="Telegram" src="https://img.shields.io/badge/Telegram-blue?&style=for-the-badge&logoColor=white&logo=telegram"/>
<img alt="Python" src="https://img.shields.io/badge/python-%2314354C.svg?&style=for-the-badge&logo=python&logoColor=white"/>
</div>

## Creating database

### Just run `create_database.py` one time.

## Setting up Telegram Account (Listener)

### You will need one Telegram Account

#### Create .env file in the project directory. .env_example file can be used as an example.

- `API_HASH` : Can be obtained here: https://my.telegram.org
- `API_ID`: Can be obtained here: https://my.telegram.org

## Configuring .txt files

- `chats.txt` : IDs/usernames of chats that must be listened
- `words.txt`: All trigger-words
- `answers.txt`: Answer messages
- `skip_words.txt`: Stop-words (trigger-words will be ignored if one appears)

#### As mentioned before, you can specify chats by ID or username.

#### In chats.txt you should not put links to public chats or usernames with https://t.me and @

#### Do it like this:

```text
durov_russia
1364081847
```

#### Answers must be separated with ===

```text
First response text

===
Second response text

===
Third response text
```

**Example files were added in order to help with configuring the user bot ❗**

### Show some ❤️ and ⭐ the repo to support the project!