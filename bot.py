"""@FoodieFunBot script."""
import os

import logging

import telegram
from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    Filters,
)

# ----------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------

# Token
TOKEN = os.getenv("TELEBOT")
PORT = int(os.environ.get("PORT", 5000))
CHANNELHANDLE = str(os.getenv("CHANNELHANDLE"))

# Stages
VIDEOBUBBLE, EMOJI, RESTAURANT, CITY, CONFIRMATION, INLINEBUTTON = range(6)

# Keyboards
start_keyboard = ["Send video bubble!"]
start_keyboard_markup = ReplyKeyboardMarkup(
    [start_keyboard],
    one_time_keyboard=True,
    input_field_placeholder="Click below 👇🏻 or /cancel convo.",
)

valid_emojis = ["🤤", "😐", "🤮"]
emoji_keyboard_markup = ReplyKeyboardMarkup(
    [valid_emojis],
    one_time_keyboard=True,
    input_field_placeholder="Choose an emoji 👇🏻.",
)

cities = ["Singapore 🇸🇬", "Kuala Lumpur 🇲🇾", "Taipei 🇹🇼"]
cities_keyboard_markup = ReplyKeyboardMarkup(
    [[city] for city in cities],
    one_time_keyboard=True,
    input_field_placeholder="Choose a city 👇🏻.",
)


def start(update: Update, context: CallbackContext) -> int:
    """
    Starts the conversation and asks the user about their gender.

    Parameters
    ----------
    update : Update
        [description]
    context : CallbackContext
        [description]
    """
    # Logging
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)

    # Store user's replies context.user_data
    context.user_data["first_name"] = user.first_name
    context.user_data["last_name"] = user.last_name
    context.user_data["video_bubble"] = None
    context.user_data["emoji"] = None
    context.user_data["restaurant"] = None
    context.user_data["city"] = None

    update.message.reply_text(
        (
            # "<i>[From context.user_data]</i>\n"
            # f"name - {context.user_data['first_name']} {context.user_data['last_name']}\n"
            # f"video_bubble: {context.user_data['video_bubble']}\n"
            # f"emoji: {context.user_data['emoji']}\n"
            # f"restaurant: {context.user_data['restaurant']}\n"
            # "----------\n"
            "👋🏻 Hello! Want to share your foodie experience?\n\n"
            "To begin, snap and send over a photo 📸.\n\n"
            "If you're stuck, use the <b>/help</b> command."
        ),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    # return VIDEOBUBBLE
    return EMOJI


def send_video(update: Update, _: CallbackContext) -> int:
    """
    Prompts the user to send a video message.

    Parameters
    ----------
    update : Update
        [description]
    context : CallbackContext
        [description]
    """
    user = update.message.from_user
    logger.info("Request for User %s to send video bubble.", user.first_name)

    # query = update.callback_query
    # query.answer()

    # query.edit_message_text(
    update.message.reply_text(
        (
            "<b>To send a video message:</b>\n"
            "1. Tap the mic icon to switch to camera mode.\n"
            "2. Tap and hold the camera icon and record a video message.\n"
            "3. Once done, release the recording button to dispatch your message.\n\n"
            "<b>FOR NOW, JUST REPLY USING TEXT E.G. 'video sent.'</b>"
        ),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    return EMOJI


def send_emoji(update: Update, context: CallbackContext) -> int:
    """
    To ask for emoji after receiving video bubble.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]

    Returns
    -------
    int
        [description]
    """
    user = update.message.from_user
    # logger.info(
    #     "Received video message from %s: %s", user.first_name, update.message.text
    # )
    # Text from send_video command.
    # text = update.message.text

    if len(update.message.photo) == 0:
        logger.info("Invalid photo from %s", user.first_name)
        update.message.reply_text(
            ("Sorry, please try to send a photo again."),
        )

        return EMOJI

    elif len(update.message.photo) > 0:
        logger.info("Received photo from %s", user.first_name)
        # photo_file.download('user_photo.jpg')

        photo_file = update.message.photo[-1].get_file()
        context.user_data["video_bubble"] = photo_file

        update.message.reply_text(
            ("Looks yummy! How would you rate this meal?"),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=emoji_keyboard_markup,
        )

    return RESTAURANT


def send_restaurant(update: Update, context: CallbackContext) -> int:
    """
    To ask for restaurant name after receiving emoji.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]

    Returns
    -------
    int
        [description]
    """
    user = update.message.from_user
    logger.info("Received emoji from %s: %s", user.first_name, update.message.text)
    # Text from send_emoji command.
    text = update.message.text

    if text not in valid_emojis:

        # Give the emoji keyboard again...
        update.message.reply_text(
            (
                f"Sorry, I don't understand what is {text}\n\n"
                "Pick one from 🤤, 😐 or 🤮 and try again."
            ),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=emoji_keyboard_markup,
        )

        # ... and go back to RESTAURANT state.
        return RESTAURANT

    elif text in valid_emojis:

        # Format emoji message:
        if text == valid_emojis[0]:
            emoji_msg = "So goood " + str(text)
        elif text == valid_emojis[1]:
            emoji_msg = "So-so " + str(text)
        elif text == valid_emojis[2]:
            emoji_msg = "Baddd " + str(text)

        # Store send_emoji reply.
        context.user_data["emoji"] = emoji_msg

        update.message.reply_text(
            (
                "Which restaurant / shop was your meal from? "
                'For example, "McDonald\'s" or "Bedok Block 85".'
            ),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
        )

        return CITY


def send_city(update: Update, context: CallbackContext) -> int:
    """
    To ask for city after receiving restaurant name.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]

    Returns
    -------
    int
        [description]
    """
    user = update.message.from_user
    logger.info(
        "Received restaurant name from %s: %s", user.first_name, update.message.text
    )
    # Text from send_emoji command.
    text = update.message.text

    # Check that restaurant name contains at least an alphanumeric character.
    if not (any(c.isalpha() for c in text) or any(c.isnumeric() for c in text)):

        update.message.reply_text(
            (
                "Sorry, restaurant name has to contain at least an alphanumeric "
                "character. Please try again!\n\n"
                "Which restaurant / shop was your meal from? "
                'For example, "McDonald\'s".'
            ),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(),
        )

        return CITY

    else:
        # Store send_restaurant reply.
        context.user_data["restaurant"] = text.strip()

        update.message.reply_text(
            ("Which city was your meal from?"),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=cities_keyboard_markup,
        )

        return CONFIRMATION


def confirmation(update: Update, context: CallbackContext) -> int:
    """
    To seek confirmation after receiving restaurant name.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]

    Returns
    -------
    int
        [description]
    """
    user = update.message.from_user
    logger.info("Received city from %s: %s", user.first_name, update.message.text)

    # Text from send_city command.
    text = update.message.text

    # Check that restaurant name contains at least an alphanumeric character.
    if text not in cities:

        update.message.reply_text(
            (
                f"Sorry, {text} is invalid at the moment. Please try again!\n\n"
                "Which city was your meal from? "
            ),
            reply_markup=cities_keyboard_markup,
        )

        return CONFIRMATION

    elif text in cities:

        # Store send_city reply.
        context.user_data["city"] = text.strip()

        keyboard = [
            [
                InlineKeyboardButton(text="Resubmit", callback_data="resubmit"),
                InlineKeyboardButton(text="Send it 👍🏻", callback_data="send"),
            ],
        ]

        # Turns the `keyboard` list into an actual inlin keyboard.
        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_photo(
            photo=context.user_data["video_bubble"]["file_id"],
            caption=(
                f"<b>Thoughts:</b> {context.user_data['emoji']}\n"
                f"<b>Restaurant:</b> {context.user_data['restaurant']} 📍\n"
                f"<b>City:</b> {context.user_data['city']}\n\n"
                f"Shared by {context.user_data['first_name']}.\n\n"
                "<i>Share your own foodie experience using @ThatBubbleBot!</i>\n"
                "----------\n\n"
                "☝🏻️ This is how your post will look."
            ),
            parse_mode=telegram.ParseMode.HTML,
            reply_markup=reply_markup,
        )

        return INLINEBUTTON


def resubmit(update: Update, context: CallbackQueryHandler) -> int:
    """
    Prompt same text as `start` does but not as new message.

    Parameters
    ----------
    update : Update
        [description]
    context : CallbackQueryHandler
        [description]

    Returns
    -------
    int
        [description]
    """
    query = update.callback_query
    query.answer()

    query.delete_message()

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Snap and send over a photo 📸.\n\n",
    )

    return EMOJI


def send_and_end(update: Update, context: CallbackContext) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    query.answer()

    query.edit_message_caption(
        caption=(
            "Hooray, it's sent!\n\n"
            "- To send a video bubble again, use <b>/start</b>.\n"
            f"- Or, return to <b>{CHANNELHANDLE}</b> channel."
        ),
        parse_mode=telegram.ParseMode.HTML,
    )

    context.bot.send_photo(
        chat_id=CHANNELHANDLE,
        photo=context.user_data["video_bubble"]["file_id"],
        caption=(
            f"<b>Thoughts:</b> {context.user_data['emoji']}\n"
            f"<b>Restaurant:</b> {context.user_data['restaurant']} 📍\n"
            f"<b>City:</b> {context.user_data['city']}\n\n"
            f"Shared by {context.user_data['first_name']}.\n\n"
            "<i>Share your own foodie experience using @ThatBubbleBot!</i>"
        ),
        parse_mode=telegram.ParseMode.HTML,
    )

    return ConversationHandler.END


def help_command(update: Update, _: CallbackContext) -> None:
    """
    /help command.
    Displays info on how to use the bot.

    Parameters
    ----------
    update : Update
        [description]
    context : CallbackContext
        [description]
    """
    user = update.message.from_user
    logger.info("User %s asked for help.", user.first_name)
    update.message.reply_text(
        text=(
            "Use <b>/start</b> to send a video bubble.\n"
            "Use <b>/cancel</b> at any time to stop the conversation."
        ),
        parse_mode=telegram.ParseMode.HTML,
        reply_to_message_id=update.message.message_id,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def unknown(update: Update, _: CallbackContext) -> None:
    """
    Handle unknown commands sent to the bot.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]
    """
    update.message.reply_text(
        (
            "Sorry, I don't understand that command. "
            "Click on <b>/help</b> to see all the available commands.\n\n"
            "Otherwise, use <b>/start</b> to send a video bubble."
        ),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def cancel(update: Update, _: CallbackContext) -> int:
    """
    /cancel command.

    Cancels after /sendvideo command.

    Parameters
    ----------
    update : Update
        [description]
    _ : CallbackContext
        [description]

    Returns
    -------
    int
        [description]
    """
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        (
            "See you next time!\n\n"
            "- To send another photo review, use <b>/start</b>.\n"
            f"- Or, return to <b>{CHANNELHANDLE}</b> channel."
        ),
        parse_mode=telegram.ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


# ----------


def main() -> None:
    """Run the bot."""

    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            VIDEOBUBBLE: [
                MessageHandler(
                    filters=Filters.regex("^(Send video bubble!)$"),
                    callback=send_video,
                )
            ],
            EMOJI: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=send_emoji,
                ),
                MessageHandler(
                    filters=Filters.photo,
                    callback=send_emoji,
                ),
            ],
            RESTAURANT: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=send_restaurant,
                )
            ],
            CITY: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=send_city,
                )
            ],
            CONFIRMATION: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,
                    callback=confirmation,
                )
            ],
            INLINEBUTTON: [
                CallbackQueryHandler(callback=resubmit, pattern="^" + "resubmit" + "$"),
                CallbackQueryHandler(callback=send_and_end, pattern="^" + "send" + "$"),
            ],
        },
        fallbacks=[
            CommandHandler(command="start", callback=start),
            CommandHandler(command="cancel", callback=cancel),
            CommandHandler(command="help", callback=help_command),
            MessageHandler(filters=Filters.command, callback=unknown),
        ],
    )

    # Add ConversationHandler to dispatcher that will be used for handling updates
    dispatcher.add_handler(conv_handler)

    unknown_handler = MessageHandler(filters=Filters.command, callback=unknown)
    dispatcher.add_handler(unknown_handler)
    help_handler = CommandHandler(command="help", callback=help_command)
    dispatcher.add_handler(help_handler)
    cancel_handler = CommandHandler(command="cancel", callback=cancel)
    dispatcher.add_handler(cancel_handler)

    # Start the Bot
    # updater.start_polling()
    updater.start_webhook(
        listen="0.0.0.0",
        port=int(PORT),
        url_path=TOKEN,
        webhook_url="https://foodiefunbot.herokuapp.com/" + TOKEN,
    )
    # updater.bot.setWebhook("https://foodiefunbot.herokuapp.com/" + TOKEN)

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == "__main__":
    main()
