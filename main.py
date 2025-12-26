import telebot
from peewee import IntegrityError
from telebot.types import Message
from typing import Dict, Union

from currencies import CURRENCIES
from config import BOT_TOKEN, API_KEY, DEFAULT_COMMANDS
import currency_api
from models import User, create_models


bot = telebot.TeleBot(BOT_TOKEN)
api_key = API_KEY


@bot.message_handler(commands=['start'])
def handle_start(message: Message) -> None:
    """ Start-function to register(validate) a current user """
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
        bot.reply_to(message, "Welcome!")
    except IntegrityError:
        bot.reply_to(message, f"Glad to see you again, {first_name}!")

    bot.send_message(message.chat.id, 'I\'m a bot for testing API integration into a Telegram bot. My name is CC. '
                                      'Particularly I\'m a currency converter. '
                                      'I can convert about 150 different currencies in real time! '
                                      '\n- To start converting process enter /convert'
                                      '\n- To return to main menu enter /home'
                                      '\n- To see user\'s data enter /user_data'
                                      '\n- To see available currencies enter /currencies'
                                      '\n- To delete current user enter /delete_current_user')


def user_exists(message: Message) -> bool:
    """ Check if user exists """
    user_id = message.from_user.id
    if User.get_or_none(User.user_id == user_id) is None:
        bot.reply_to(message, "You're not registered. Enter /start")
        return False
    return True


@bot.message_handler(commands=['home'])
def return_home(message: Message) -> None:
    """ Return to main menu """
    handle_start(message)


@bot.message_handler(commands=['user_data'])
def get_user(message: Message) -> None:
    """ Get user's data """
    user_id = message.from_user.id
    if not user_exists(message):
        return
    bot.send_message(message.chat.id, User.get(User.user_id == user_id))



def command_check(message: Message) -> bool:
    """ Check if entered message is a command """
    if message.text.startswith('/'):
        users_input = message.text.lstrip('/').lower()
        for i_command in DEFAULT_COMMANDS:
            if users_input == i_command[0]:
                return True
    return False


def send_long_message(bot, chat_id, lines, parse_mode=None) -> None:
    """ Function to send a long message """
    max_len = 4096
    result = ''

    for i_line in lines:
        if len(result) + len(i_line) + 1 > max_len:
            bot.send_message(chat_id, result, parse_mode=parse_mode)
            result = i_line + '\n'
        else:
            result += i_line + '\n'

    if result:
        bot.send_message(chat_id, result, parse_mode=parse_mode)


@bot.message_handler(commands=['currencies'])
def get_currencies(message: Message) -> None:
    bot.send_message(message.chat.id, 'List of all available currencies to convert:')
    send_long_message(bot, message.chat.id, currency_api.get_currencies())


@bot.message_handler(commands=['convert'])
def start_convert(message: Message) -> None:
    """ Function for getting currency from which program is going to convert """
    if not user_exists(message):
        return

    msg = bot.send_message(message.chat.id, 'Enter the currency code from which you want to convert'
                                            '(in case if you want to see available currencies enter /currencies):')
    bot.register_next_step_handler(msg, get_currency_to)


def get_currency_to(message: Message) -> None:
    """ Function for getting currency to which program is going to convert """
    if command_check(message):
        bot.process_new_messages([message])
        return
    change_from = message.text.upper()
    if change_from not in CURRENCIES:
        retry = bot.send_message(message.chat.id, 'Invalid currency code. Try again:')
        bot.register_next_step_handler(retry, get_currency_to)
        return

    msg = bot.send_message(message.chat.id, 'Enter the currency code to which you want to convert'
                                            '(in case if you want to see available currencies enter /currencies):')
    bot.register_next_step_handler(msg, get_amount, change_from)


def get_amount(message: Message, change_from: str) -> None:
    """ Function for getting value which is going to convert """
    if command_check(message):
        bot.process_new_messages([message])
        return
    change_to = message.text.upper()
    if change_to not in CURRENCIES:
        retry = bot.send_message(message.chat.id, 'Invalid currency code. Try again:')
        bot.register_next_step_handler(retry, get_currency_to, change_from)
        return

    msg = bot.send_message(message.chat.id, 'Enter the amount you want to convert:')
    bot.register_next_step_handler(msg, final_convert, change_from, change_to)


def final_convert(message: Message, convert_from: str, convert_to: str) -> Union[Dict, None]:
    """ Final step of converting with API request """
    if command_check(message):
        bot.process_new_messages([message])
        return
    try:
        amount = message.text
        result = currency_api.convert_currency(convert_from, convert_to, float(amount))
        if result["error"] != 0:
            bot.send_message(message.chat.id, "Currency conversion failed.")
            return
        bot.send_message(message.chat.id, '{amount} {c_from} in {c_to} equals {res}'.format(
            amount=amount,
            c_from=convert_from,
            c_to=convert_to,
            res=round(result['amount'], 2)
        ))
    except TypeError:
        bot.send_message(message.chat.id, 'Something went wrong. '
                                               'Entered value is possibly not a digit. Try again:')
        get_amount(message, convert_from)


@bot.message_handler(commands=['delete_current_user'])
def delete_current_user(message: Message) -> None:
    """ Function for deleting current user """
    if not user_exists(message):
        return
    bot.send_message(message.chat.id, 'Successfully deleted current user.')
    user_id = message.from_user.id
    User.delete().where(User.user_id == user_id).execute()



@bot.message_handler(func=lambda message: True)
def undefined_function(message: Message) -> None:
    """ Navigation in case if entered text is undefined """
    users_input = message.text.lstrip('/').lower()
    for i_command in DEFAULT_COMMANDS:
        if users_input == i_command[0]:
            return
    else:
        bot.reply_to(message, 'Undefined command.\nHere are all available commands:\n'
                                    '\n- To start converting process enter /convert'
                                    '\n- To return to main menu enter /home'
                                    '\n- To see user\'s data enter /user_data'
                                    '\n- To see available currencies enter /currencies'
                                    '\n- To delete current user enter /delete_current_user')



if __name__ == '__main__':
    create_models()
    bot.set_my_commands([telebot.types.BotCommand(command[0], command[1]) for command in DEFAULT_COMMANDS])
    bot.infinity_polling()



