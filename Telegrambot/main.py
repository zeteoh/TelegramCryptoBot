import os
from flask import Flask, request, Response
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Set up Telegram bot API
TELEGRAM_API_TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(TELEGRAM_API_TOKEN)

# Initialize global variable for chat ID
user_chat_id = None


@app.route('/notify', methods=['POST'])
def notify():
    # Extract logs from request
    logs = request.json['event']['data']['block']['logs']

    # Check if logs array is empty
    if len(logs) == 0:
        print("Empty logs array received, skipping")
    else:
        # Loop through each log in the logs array
        for i in range(0, len(logs)):
            # Extract topic1, topic2, and amount from the log
            topic1 = "0x" + logs[i]['topics'][1][26:]
            topic2 = "0x" + logs[i]['topics'][2][26:]
            amount = "{:.3f}".format(int(logs[i]['data'], 16) / float(1e18))

            # Create message to send to Telegram
            message = topic1 + ' sent ' + amount + ' DAI to ' + topic2

            # Send the message to the user
            if user_chat_id is not None:
                bot.send_message(chat_id=user_chat_id, text=message)
            else:
                print("User chat ID not set, skipping message")

    # Return a success response to the request
    return Response(status=200)


def start(update: Update, context: CallbackContext):
    global user_chat_id
    user_chat_id = update.effective_chat.id
    update.message.reply_text("You will now receive notifications.")


# Set up the webhook
def set_webhook():
    # set ngok web hook url ending with /notify
    webhook_url = '/notify'
    updater.bot.set_webhook(webhook_url)


updater = Updater(TELEGRAM_API_TOKEN)
updater.dispatcher.add_handler(CommandHandler("start", start))

# Uncomment the line below to set up the webhook
set_webhook()
# updater = Updater(TELEGRAM_API_TOKEN)
# updater.dispatcher.add_handler(CommandHandler("start", start))

# Start the bot
updater.start_polling()

# Start Flask app
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
