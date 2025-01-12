import logging
from typing import Any

from telegram import Update
from telegram.ext import CallbackContext, ContextTypes, JobQueue

import config
from scraper import Scraper


class BotManager:
    def __init__(self, job_queue: JobQueue, scraper: Scraper):
        """
        Initializes the BotManager with a job queue and a scraper instance.
        """
        self.job_queue = job_queue
        self.scraper = scraper
        self.jobs: dict[int, Any] = {}

    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles the /start command. Sends a menu with available commands.
        """
        await update.message.reply_text(
            "Menu:\n"
            "1. Démarrer la vérification des RDV : /demarrer\n"
            "2. Arrêter la vérification des RDV : /arreter\n"
            "3. Définir la fréquence : /freq <seconds>\n"
        )

    async def handle_start_checking(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handles the /demarrer command. Starts checking for appointments.
        """
        if update is None or context is None:
            return
        chat_id = update.message.chat_id
        response = self.start_checking(chat_id)
        await update.message.reply_text(response)

    async def handle_stop_checking(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handles the /arreter command. Stops checking for appointments.
        """
        chat_id = update.message.chat_id
        response = self.stop_checking(chat_id)
        await update.message.reply_text(response)

    async def handle_set_frequency(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ):
        """
        Handles the /freq command. Sets the frequency for checking appointments.
        """
        chat_id = update.message.chat_id
        try:
            interval = int(context.args[0])
            response = self.set_frequency(chat_id, interval)
            await update.message.reply_text(response)
        except (IndexError, ValueError):
            await update.message.reply_text("Usage: /freq <seconds>")

    async def check_appointments(self, context: CallbackContext):
        """
        Checks for available appointments and sends a message if any are found.
        """
        try:
            html_content = await self.scraper.scrape()
            if not html_content:
                return
            available_slots = self.scraper.extract_appointments(html_content)

            if available_slots:
                message = (
                    f"{len(available_slots)} rendez-vous disponibles !\n"
                    + "\n".join(available_slots)
                )
                await context.bot.send_message(chat_id=context._chat_id, text=message)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")

    def start_checking(self, chat_id: int):
        """
        Starts the job for checking appointments at the default frequency.
        """
        if chat_id in self.jobs:
            return "La vérification des rendez-vous est déjà en cours."
        job = self.job_queue.run_repeating(
            self.check_appointments,
            interval=config.DEFAULT_FREQUENCY,
            first=10,
            chat_id=chat_id,
        )
        self.jobs[chat_id] = job
        return (
            f"Recherche des RDV en cours, fréquence par défaut : {config.DEFAULT_FREQUENCY // 60} min. "
            "Vous pouvez modifier la fréquence en faisant /freq <seconds>."
        )

    def stop_checking(self, chat_id: int):
        """
        Stops the job for checking appointments.
        """
        if chat_id not in self.jobs:
            return "La recherche de RDV est à l'arrêt. Pour démarrer, saisissez la commande /demarrer."
        self.jobs[chat_id].schedule_removal()
        del self.jobs[chat_id]
        return "La vérification des rendez-vous a été arrêtée."

    def set_frequency(self, chat_id: int, interval: int):
        """
        Sets a new frequency for checking appointments.
        """
        if chat_id not in self.jobs:
            return "La recherche de RDV est à l'arrêt. Pour démarrer, saisissez la commande /demarrer."
        self.jobs[chat_id].schedule_removal()
        job = self.job_queue.run_repeating(
            self.check_appointments,
            interval=interval,
            chat_id=chat_id,
        )
        self.jobs[chat_id] = job
        return f"Votre fréquence a été modifiée avec succès. Le bot recherchera des RDV chaque {interval} secondes et vous notifiera s'il trouve un RDV."
