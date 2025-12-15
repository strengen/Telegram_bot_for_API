import telebot
from peewee import IntegrityError
from telebot.types import Message
from typing import Dict, Union

from currencies import CURRENCIES
from config import BOT_TOKEN, API_KEY
import currency_api
from models import User, create_models


bot = telebot.TeleBot(BOT_TOKEN)
api_key = API_KEY


@bot.message_handler(commands=['start'])
def handle_start(message: Message) -> None:
    """Start-function for registering(validating) a current user with greetings"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    try:
        User.create(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        bot.reply_to(message, "Wellcome!")
    except IntegrityError:
        bot.reply_to(message, f"Glad to see you again, {first_name}!")

    bot.send_message(message.chat.id, 'I\'m a bot for testing API integration into a Telegram bot. My name is CC. '
                                      'Particularly I\'m a currency converter. '
                                      'I can convert about 150 different currencies in real time! '
                                      'To start converting process enter "/convert"'
                                      'To return to main menu enter "/home"'
                                      'To see user\'s data enter "/user_data"')

@bot.message_handler(commands=['home'])
def return_home(message: Message) -> None:
    """Return to main menu"""
    handle_start(message)

@bot.message_handler(commands=['user_data'])
def get_user(message: Message) -> None:
    """Get user's data"""
    user_id = message.from_user.id
    bot.send_message(message.chat.id, User.get(User.user_id == user_id))

@bot.message_handler(commands=['convert'])
def send_convert(message: Message) -> None:
    """ Function for getting currency from which program is going to convert """
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "You're not registered. Enter /start")
        return

    bot.send_message(message.chat.id, f'List of all available currencies to convert: {currency_api.get_currencies()}')
    msg = bot.send_message(message.chat.id, 'Enter the currency code from which you want to convert:')

    bot.register_next_step_handler(msg, get_currency_to)

def get_currency_to(message: Message) -> None:
    """ Function for getting currency to which program is going to convert """
    change_from = message.text.upper()
    if change_from not in CURRENCIES:
        retry = bot.send_message(message.chat.id, 'Invalid currency code. Try again:')
        bot.register_next_step_handler(retry, get_currency_to)
        return

    msg = bot.send_message(message.chat.id, 'Enter the currency code to which you want to convert:')
    bot.register_next_step_handler(msg, get_amount, change_from)

def get_amount(message: Message, change_from: str) -> None:
    """ Function for getting value which is going to convert """
    change_to = message.text.upper()
    if change_to not in CURRENCIES:
        retry = bot.send_message(message.chat.id, 'Invalid currency code. Try again:')
        bot.register_next_step_handler(retry, get_currency_to, change_from)
        return

    msg = bot.send_message(message.chat.id, 'Enter the amount you want to convert:')
    bot.register_next_step_handler(msg, final_convert, change_from, change_to)


def final_convert(message: Message, convert_from: str, convert_to: str) -> Union[Dict, None]:
    """Final step of converting with API request"""
    try:
        amount = message.text
        result = currency_api.convert_currency(convert_from, convert_to, float(amount))
        if result["error"] != 0:
            bot.send_message(message.chat.id, "Currency conversion failed.")
            return
        bot.send_message(message.chat.id, f'{amount} {convert_from} in {convert_to} equals {result['amount']}')
    except Exception:
        bot.send_message(message.chat.id, 'Something went wrong. '
                                               'Entered value is possibly not a digit. Try again:')
        get_amount(message, convert_from)




if __name__ == '__main__':
    create_models()
    bot.set_my_commands([telebot.types.BotCommand('start', 'Start'),
                         telebot.types.BotCommand('home', 'Home page'),
                         telebot.types.BotCommand('user_data', 'Get user\'s data'),
                         telebot.types.BotCommand('convert', 'Convert currency'),])
    bot.infinity_polling()



