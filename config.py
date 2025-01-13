import os

from dotenv import load_dotenv

load_dotenv()

# URL for the appointment slots
URL = os.getenv(
    "URL",
    "https://esii-orion.com/orion-reservation/slots?account=EVMSPI&config=SEJOURREMISE&usemode=app",
)

# Default frequency for checking appointments in seconds
DEFAULT_FREQUENCY = int(os.getenv("DEFAULT_FREQUENCY", 1800))

# Path to Chromium executable
CHROMIUM_PATH = os.getenv(
    "PUPPETEER_EXECUTABLE_PATH",
    "/usr/bin/chromium",
)

# Path to SQLite database
DATABASE_PATH = os.getenv("DATABASE_PATH", "appointments.db")
