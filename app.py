import asyncio
import csv
import logging
import os
import signal
from io import BytesIO, StringIO

from dotenv import load_dotenv
from flask import Flask, render_template, send_file

from csv_exporter import CSVExporter
from database import Database
from job_manager import JobManager
from scraper import Scraper

load_dotenv()

app = Flask(__name__)
db = Database()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


@app.route("/")
def index():
    appointments = db.get_appointments()
    data = [
        {"date": date, "time": time, "location": location}
        for date, time, location in appointments
    ]
    return render_template("index.html", appointments=data)


@app.route("/export")
def export():
    appointments = db.get_appointments()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["Date", "Time", "Location"])
    cw.writerows(appointments)
    si.seek(0)
    byte_data = BytesIO(si.getvalue().encode("utf-16"))
    return send_file(
        path_or_file=byte_data,
        mimetype="text/csv",
        as_attachment=True,
        download_name="appointments.csv",
    )


async def start_flask():
    loop = asyncio.get_event_loop()
    try:
        await loop.run_in_executor(None, app.run, "127.0.0.1", 5000, False)
    except OSError as e:
        if "Address already in use" in str(e):
            logging.error(
                "Port 5000 is already in use. Please free the port or use a different one."
            )
            raise SystemExit(1)


async def main():
    """
    Main function to start the Flask app and JobManager in parallel.
    """
    scraper = Scraper()
    csv_exporter = CSVExporter()
    job_manager = JobManager(scraper=scraper, db=db, exporter=csv_exporter)

    job_manager_task = asyncio.create_task(job_manager.run())
    flask_task = asyncio.create_task(start_flask())

    def shutdown():
        logging.info("Received shutdown signal, cancelling tasks...")
        job_manager_task.cancel()
        flask_task.cancel()
        os._exit(1)

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, shutdown)
    loop.add_signal_handler(signal.SIGTERM, shutdown)

    try:
        await asyncio.gather(job_manager_task, flask_task)
    except asyncio.CancelledError:
        logging.info("Tasks have been cancelled.")
        shutdown()
    except SystemExit:
        shutdown()


if __name__ == "__main__":
    asyncio.run(main())
