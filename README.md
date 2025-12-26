# Telegram Currency Converter Bot

Telegram bot for currency conversion using an external API and a local database.

This project was created for educational purposes and demonstrates working with the Telegram Bot API, HTTP requests, ORM, and environment variables.

## Features

- Currency conversion using up-to-date exchange rates  
- Dialog-based interaction with the user  
- User input validation and error handling  
- Integration with an external currency API (Amdoren)  
- User data storage using SQLite and Peewee ORM  
- Configuration via environment variables (.env)


## Installation and Setup

1. Clone the repository:

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a .env file in the project root with the following variables:
```env
BOT_TOKEN=your_telegram_bot_token
API_KEY=your_amdoren_api_key
DB_PATH=database.db
```

After running the bot will be available in Telegram.

## How It Works

The user selects the source and target currencies, enters an amount, and the bot sends a request to the external API. The response is processed and the converted value is returned to the user. User data is stored in a local SQLite database.

## Notes

The project does not contain any sensitive data. The .env file is excluded from version control via .gitignore.
