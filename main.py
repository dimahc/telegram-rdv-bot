import logging

from telegram import BotCommand
from telegram.ext import ApplicationBuilder, CommandHandler

import config
from bot_manager import BotManager
from scraper import Scraper

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


async def set_commands(application):
    """
    Sets the bot commands for the Telegram bot.
    """
    commands = [
        BotCommand("start", "Afficher le menu principal"),
        BotCommand("demarrer", "Démarrer la vérification des RDV"),
        BotCommand("arreter", "Arrêter la vérification des RDV"),
        BotCommand("freq", "Définir la fréquence de vérification (en secondes)"),
    ]
    await application.bot.set_my_commands(commands)


def main():
    """
    Main function to start the Telegram bot application.
    """
    application = ApplicationBuilder().token(config.TOKEN).build()
    scraper = Scraper()
    bot_manager = BotManager(application.job_queue, scraper)

    # Add command handlers
    application.add_handler(CommandHandler("start", bot_manager.handle_start))
    application.add_handler(
        CommandHandler("demarrer", bot_manager.handle_start_checking)
    )
    application.add_handler(CommandHandler("arreter", bot_manager.handle_stop_checking))
    application.add_handler(CommandHandler("freq", bot_manager.handle_set_frequency))

    # Set up commands menu
    application.job_queue.run_once(set_commands, 1, application)

    application.run_polling()


if __name__ == "__main__":
    main()
