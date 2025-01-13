import asyncio
import logging

import config
from csv_exporter import CSVExporter
from database import Database
from scraper import Scraper


class JobManager:

    def __init__(
        self,
        scraper=Scraper(),
        db=Database(),
        exporter=CSVExporter(),
        interval=config.DEFAULT_FREQUENCY,
    ):
        """
        Initializes the JobManager with a scraper, database, and CSV exporter.
        """
        self.scraper = scraper
        self.exporter = exporter
        self.db = db
        self.interval = interval  # Default interval of 300 seconds (5 minutes)
        self._running = True
        self.job_queue: set[asyncio.Task[None]] = set()

    async def save_appointments(self):
        """
        Checks for available appointments and saves them in the database.
        """
        try:
            html_content = await self.scraper.scrape()
            if not html_content:
                return
            available_slots = self.scraper.extract_appointments(html_content)

            if available_slots:
                formatted_appointments = [
                    (slot["date"], slot["time"], slot["location"])
                    for slot in available_slots
                ]
                self.db.save_appointments(formatted_appointments)
        except Exception as e:
            logging.error(f"An error occurred during appointment scraping: {str(e)}")

    async def export_appointments_to_csv(self):
        """
        Exports available appointments to a CSV file.
        """
        try:
            appointments = self.db.get_appointments()
            if appointments:
                self.exporter.export(data=appointments)
        except Exception as e:
            logging.error(f"An error occurred while exporting appointments: {str(e)}")

    def set_frequency(self, interval: int):
        """
        Sets a new frequency for checking appointments.
        """
        self.interval = interval

    def stop(self, signum, frame):
        """
        Stops the job manager gracefully.
        """
        logging.info("Received termination signal, stopping...")
        self._running = False
        for task in self.job_queue:
            task.cancel()

    async def run(self):
        """
        Runs the job manager and schedules tasks to run at regular intervals.
        """
        logging.info("Starting job manager...")
        while self._running:
            try:
                await self.save_appointments()
                await self.export_appointments_to_csv()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                logging.info("Job manager stopped.")
                break
            except Exception as e:
                logging.error(f"An error occurred during job execution: {str(e)}")
                await asyncio.sleep(self.interval)
