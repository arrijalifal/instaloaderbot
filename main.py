import instaloader
from instaloader import exceptions
from pathlib import Path
from cred import TELEGRAM_TOKEN
import telegram
from telegram import Update, MessageEntity, InputMediaPhoto, InputMediaVideo
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)
from urllib.parse import urlparse
from datetime import datetime

# Telegram Initializer
updater = Updater(TELEGRAM_TOKEN)
# Get instance
L = instaloader.Instaloader()

# Optionally, login or load session

try:
    L.load_session_from_file(username="arrijal.ifal", filename="session/sessionfile")
except FileNotFoundError:
    try:
        USERNAME = input("Input your Username = ")
        L.interactive_login(USERNAME)
    except exceptions.TwoFactorAuthRequiredException():
        f_a = input("2FA = ")
        L.two_factor_login(f_a)
finally:
    L.save_session_to_file()


# Telegram Functions
def hello(update: Update, context: CallbackContext):
    update.message.reply_text(f"Hello {update.effective_user.first_name}")


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def caps(update: Update, context: CallbackContext):
    text_caps = ' '.join(context.args).upper()
    context.bot.send_message(chat_id=update.effective_chat.id, text=context.args)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)


def download_image(update: Update, context: CallbackContext):
    for entity in update.message.entities:
        if entity.type == "url":
            url = urlparse(update.message.parse_entity(entity)).path.split('/')[2]
            loading = update.message.reply_text(f"<i>Downloading info from URL. Please wait...</i>",
                                                parse_mode=telegram.ParseMode.HTML)
            now = datetime.now()
            user_now = f"{now.year}{now.month}{now.day}{now.hour}{now.minute}{now.second}"
            path = Path(f"{update.effective_user.id}/{user_now}")
            post = instaloader.Post.from_shortcode(L.context, url)
            if L.download_post(post, path):
                mediafiles = []
                for files in path.glob("*"):
                    if str(files).endswith(".jpg"):
                        mediafiles.append(InputMediaPhoto(media=open(str(files), "rb")))
                    elif str(files).endswith(".mp4"):
                        mediafiles.append(InputMediaVideo(media=open(str(files), "rb")))
                    elif str(files).endswith(".txt"):
                        with open(str(files), encoding="utf8") as capt:
                            textcaption = capt.read()
                context.bot.sendMediaGroup(chat_id=update.effective_user.id,
                                           media=mediafiles
                                           )
                update.message.reply_text(textcaption)
            else:
                update.message.edit_text("Can't reach the URL!")


# Telegram Command Handler
updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(MessageHandler(Filters.text, download_image))
updater.dispatcher.add_handler(CommandHandler('caps', caps))
updater.start_polling()
