import ramadhan_sahur
from telegram import Updater
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import logging
import requests
import json

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Set up API credentials
MIDTRANS_SERVER_KEY = ' '
MIDTRANS_CLIENT_KEY = ' '

# Define the available packages
PACKAGES = [
    {
        'name': 'Paket 7hr',
        'price': 150000,
        'id': 'package_7hr'
    },
    {
        'name': 'Paket 15hr',
        'price': 175000,
        'id': 'package_15hr'
    },
    {
        'name': 'Paket 30hr',
        'price': 300000,
        'id': 'package_30hr'
    },
    {
        'name': 'Sayang',
        'price': 10000,
        'id': 'add_on_sayang'
    },
    {
        'name': 'Bebeb',
        'price': 15000,
        'id': 'add_on_bebek'
    }
]

# Define the command to start the bot
def start(update, context):
    # Send a welcome message with the available packages
    message = "Selamat datang di bot jasa bangunin sahur dan ingetin buka puasa. Berikut adalah paket yang tersedia:\n\n"
    for package in PACKAGES:
        message += f"{package['name']} : Rp. {package['price']}\n"
    message += "\nSilakan pilih paket yang Anda inginkan dengan menekan tombol di bawah ini."
    # Create the keyboard with the available packages
    keyboard = [[ramadhan_sahur.InlineKeyboardButton(package['name'], callback_data=package['id'])] for package in PACKAGES]
    reply_markup = ramadhan_sahur.InlineKeyboardMarkup(keyboard)
    # Send the message with the keyboard
    update.message.reply_text(text=message, reply_markup=reply_markup)

# Define the callback function for when a package is selected
def package_selected(update, context):
    # Get the selected package
    selected_package_id = update.callback_query.data
    selected_package = next((package for package in PACKAGES if package['id'] == selected_package_id), None)
    if selected_package is None:
        # If the selected package is not found, send an error message
        message = "Maaf, paket yang Anda pilih tidak tersedia. Silakan coba lagi."
        update.callback_query.answer(text=message)
        return
    # Create the Midtrans payment link
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'Basic {MIDTRANS_SERVER_KEY}'
    }
    payload = {
        'transaction_details': {
            'order_id': update.callback_query.from_user.id,
            'gross_amount': selected_package['price']
        },
        'item_details': [
            {
                'id': selected_package['id'],
                'name': selected_package['name'],
                'price': selected_package['price'],
                'quantity': 1
            }
        ],
        'credit_card': {
            'secure': True
        }
    }
    payment_link_response = requests.post('https://api.midtrans.com/v2/charge', headers=headers, data=json.dumps(payload))
    if payment_link_response.status_code != 201:
        # If there is an error creating the payment link, send an error message
        message = "Maaf, terjadi kesalahan saat membuat tautan pembayaran. Silakan coba lagi."
        update.callback_query.answer(text=message)
        return
    payment_link = payment_link_response.json()['redirect_url']
    # Send the payment link
    message = f"Silakan klik tautan berikut untuk melakukan pembayaran:\n\n{payment_link}\n\nSetelah melakukan pembayaran, silakan kirimkan bukti pembayaran ke nomor WA kami: 08123456789"
    update.callback_query.answer(text=message)

# Set up the bot and add the handlers
def main():
    updater = Updater('TOKEN DDARI BOT FATHER', use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(package_selected))
    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
