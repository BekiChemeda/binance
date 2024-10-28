import telebot
from telebot import TeleBot, types
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()
BOT_TOKEN = os.getenv('API_TOKEN')

PORT = int(os.environ.get('PORT', 8000))  # Get the port from the environment variable or use 8000 as default

bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)



def store_user_id(user_id):
    # Check if the file exists
    if not os.path.exists('user_ids.csv'):
        # Create a new DataFrame and save it
        df = pd.DataFrame(columns=['user_id'])
        df.to_csv('user_ids.csv', index=False)

    # Load existing user IDs
    df = pd.read_csv('user_ids.csv')

    # Add the new user ID if not already present
    if user_id not in df['user_id'].values:
        df = df._append({'user_id': user_id}, ignore_index=True)
        df.to_csv('user_ids.csv', index=False)


def check_membership(user_id):
    try:
        member_bright_codes = bot.get_chat_member('@Bright_Codes', user_id)
        member_et_cryptopia = bot.get_chat_member('@Et_Cryptopia', user_id)
        return member_bright_codes.status in ['member', 'administrator', 'creator'] and member_et_cryptopia.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False
# Fetch Binance data
def get_data():
    url = "https://ethiopian-currency-exchange.vercel.app/"
    res = requests.get(url).json()
    best_rate = res['bestRates'][3]
    global buy_rate, sell_rate
    buy_rate = best_rate['buyRate']
    sell_rate = best_rate['sellRate']

    return (
        f"<b>Platform: <a href='https://www.binance.info/activity/referral-entry/CPA/together-v4?hl=en&ref=CPA_00II2YH68T'> Binance</a></b>\n"
        f"Base Currency: <b>{best_rate['baseCurrency']}</b>\n"
        f"Currency Code: <b>{best_rate['currencyCode']}</b>\n"
        f"Buy Rate: {buy_rate} ETB\n"
        f"Sell Rate: {sell_rate} ETB\n"
        f"Buy-Sell Difference: {best_rate['buySellDifference']} ETB\n"
        f"Last Updated: {res['lastUpdated']}\n\n\n"
        f"📢 Channel : @Et_Cryptopia\n"
        f"💻Developer : @BEK_I"
    )
@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200
# Start command
# Start command
@bot.message_handler(commands=['start', 'Start'])
def start_command(message):
    user_id = message.from_user.id
    store_user_id(user_id)

    # Create inline keyboard
    keyboard = types.InlineKeyboardMarkup()
    join_channel_button = types.InlineKeyboardButton("📢 Bright Codes", url='https://t.me/Bright_Codes')
    join_channel_button2 = types.InlineKeyboardButton("📢 Cryptopia", url='https://t.me/Et_Cryptopia')
    check_membership_button = types.InlineKeyboardButton("🟢 Check Membership", callback_data='check_membership')

    keyboard.add(join_channel_button, join_channel_button2)
    keyboard.add(check_membership_button)

    if not check_membership(user_id):
        bot.reply_to(message, "You must be a member of Below Channels In order to Use this Bot. \n @Bright_Codes \n @Et_Cryptopia", reply_markup=keyboard)
        return

    # Enhanced welcome message
    welcome_message = ('''👋 Greetings! Welcome to the Binance P2P Exchange Rates Bot. This bot provides you with real-time Price Of USDT on Binance P2P.
You can check the current rates, convert currencies, and get assistance with commands. Type /help to get list of Available Commands 


Retrieving the latest rates...'''

    )

    bot.reply_to(message, welcome_message)

    result = get_data()  # Assuming get_data() is defined elsewhere
    bot.send_message(message.chat.id, result, parse_mode="HTML", disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data == 'check_membership')
def check_membership_callback(call):
    user_id = call.from_user.id
    if check_membership(user_id):
        # Automatically start the bot by calling start_command
        bot.answer_callback_query(call.id, "You are a member! Starting...")

        # Simulate sending /start command
        start_command(call.message)
    else:
        bot.answer_callback_query(call.id, "You are NOT a member of the required channels. Please join first.")


# Help command
@bot.message_handler(commands=['help', 'Help'])
def help_command(message):
    donate_keyboard = types.InlineKeyboardMarkup()
    donate_button = types.InlineKeyboardButton("💳 Donate", callback_data='donate')
    donate_keyboard.add(donate_button)
    help_text = ("<b>Available Commands</b>\n"
                 "/start - Refresh The Bot\n"
                 "/about - About the Bot\n"
                 "/help - Display assistance options\n"
                 "/convUSDT - Convert USDT to ETB\n"
                 "/convETB - Convert ETB to USDT")
    bot.send_message(message.chat.id, help_text, parse_mode="HTML", reply_markup=donate_keyboard)



@bot.message_handler(commands=['about', 'ABOUT'])
def send_about(message):
    about_message = """
<b>Welcome to Binance Rates v1.0!</b>
This bot is designed to provide you with the latest <b>USDT to ETB</b> exchange rates, making your currency conversions quick and easy.

Exciting news! I have plans for an update in just <b>4 days</b>. After my <b>Model Exam</b> (wish me luck! 😁), I’ll be releasing the next version, which will include additional features to enhance your experience.

I want to be transparent with you: I know this bot can be slow at times and may even avoid answering occasionally. This is due to limitations of the free hosting service I'm using. To improve performance and ensure <b>24/7 accessibility</b>, I would greatly appreciate your support. If you'd like to help, please consider donating through the button below.

Thank you for your understanding and support!

Our channel 📢: <a href="https://t.me/Et_Cryptopia">@Et_Cryptopia</a>

Developer 🧑‍💻: <a href="https://t.me/BEK_I">@BEK_I</a>

Dev Channel 🧑‍💻: <a href="https://t.me/Bright_Codes">@Bright_Codes</a>
    """
    donate_keyboard = types.InlineKeyboardMarkup()
    donate_button = types.InlineKeyboardButton("💳 Donate", callback_data='donate')
    donate_keyboard.add(donate_button)

    bot.send_message(message.chat.id, about_message, parse_mode='HTML', reply_markup=donate_keyboard, disable_web_page_preview=True)

# Convert USDT to ETB
@bot.message_handler(commands=['convUSDT', 'ConvUSDT', 'CONVUSDT', 'convusdt'])
def convert_usdt_to_etb(message):
    donate_keyboard = types.InlineKeyboardMarkup()
    donate_button = types.InlineKeyboardButton("Donate", callback_data='donate')
    donate_keyboard.add(donate_button)
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        amount = float(args[1])
        get_data()
        buy_price = amount * buy_rate
        sell_price = amount * sell_rate
        response = (f"Converting {amount} USDT to ETB...\n"
                    f"Binance Exchange USDT Rate\n"
                    f"Buy Rate: {buy_price} ETB\n"
                    f"Sell Rate: {sell_price} ETB")
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=donate_keyboard)
    else:
        bot.send_message(message.chat.id, "Please use the following format: /convUSDT [amount]", reply_markup=donate_keyboard)

# Convert ETB to USDT
@bot.message_handler(commands=['convETB', 'ConvETB', 'CONVETB','convetb'])
def convert_etb_to_usdt(message):
    donate_keyboard = types.InlineKeyboardMarkup()
    donate_button = types.InlineKeyboardButton("Donate", callback_data='donate')
    donate_keyboard.add(donate_button)
    args = message.text.split()
    if len(args) == 2 and args[1].isdigit():
        amount = float(args[1])
        get_data()
        buy_price = amount / buy_rate
        sell_price = amount / sell_rate
        response = (f"Converting {amount} ETB to USDT...\n"
                    f"You may buy: {buy_price} USDT with {amount} ETB, or sell for {sell_price} USDT")
        bot.send_message(message.chat.id, response, parse_mode="HTML", reply_markup=donate_keyboard)
    else:
        bot.send_message(message.chat.id, "Please use the following format: /convETB [amount]", reply_markup=donate_keyboard)

@bot.callback_query_handler(func=lambda call: call.data == 'donate')
def donate_callback(call):
    # Your crypto addresses
    crypto_addresses = (
        '''<b>Support Our Development!</b>

Thank you for using Binance Rates v1.0! Your support is vital for keeping this bot running smoothly and improving its features.

Currently, this bot is hosted on a free service, which can sometimes lead to performance issues. By contributing, you help us upgrade to a reliable hosting solution, ensuring <b>faster response times</b> and <b>24/7 availability</b>.

If you would like to support us, please consider donating using the addresses below:

<b>Telebirr:</b>
<code>+251904253864</code>

<b>USDT (Trc 20):</b>
<code>TXjnroubMzwx3fxqiQg2x6uNzcJUsKa5b7</code>

<b>USDT (TON Network):</b>
<code>EQD5mxRgCuRNLxKxeOjG6r14iSroLF5FtomPnet-sgP5xNJb</code>
Memo: <code>106749170</code>

<b>USDT (BEP 20):</b>
<code>0x9647bd1c80ba188f87c29f5e7949f1a1d048e026</code>

<b>USDT (ERC 20):</b>
<code>0x9647bd1c80ba188f87c29f5e7949f1a1d048e026</code>

<b>NOT (TON):</b>
<code>EQD5mxRgCuRNLxKxeOjG6r14iSroLF5FtomPnet-sgP5xNJb</code>
Memo: <code>106749170</code>

<b>DOGS (TON):</b>
<code>EQD5mxRgCuRNLxKxeOjG6r14iSroLF5FtomPnet-sgP5xNJb</code>
Memo: <code>106749170</code>

<b>Bitcoin:</b>
<code>1EkS5c1aTXrDbrbtimbCeahz8Vdi39wWyG</code>

Every contribution, no matter how small, makes a significant difference. Thank you for your generosity!

For any questions or further information, feel free to reach out!

<b>Our channel:</b> <a href="https://t.me/Et_Cryptopia">@Et_Cryptopia</a>
'''
    )

    bot.answer_callback_query(call.id, "Here are our crypto addresses:")
    bot.send_message(call.message.chat.id, crypto_addresses, parse_mode="html")

# Start polling
bot.remove_webhook()  # Remove any existing webhook
bot.set_webhook(url='https://spatial-natka-brightcodes-c01c5910.koyeb.app/webhook')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
    print("Bot is running...")

