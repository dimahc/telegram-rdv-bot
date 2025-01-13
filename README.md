# Rennes Prefecture Appointment Scraper

This application scrapes appointment data for resident permit delivery from the Rennes prefecture website. The scraped data is stored in a database and can be viewed on a website or exported as a CSV file.

## Features

- Scrapes appointment data from the Rennes prefecture website.
- Stores the scraped data in a SQLite database.
- Displays the appointment data on a web interface.
- Exports the appointment data to a CSV file.

## Configuration

Before running the app, make sure to configure the following variables in the `config.py` file:
- `URL`: The URL of the Rennes prefecture appointment page.
- `DEFAULT_FREQUENCY`: The interval between each request to the appointment page.
- `CHROMIUM_PATH`: The path to the Chromium executable or leave it empty if using the default system path.

**Note**: Setting the frequency of appointment checking too high may result in excessive load on the Rennes prefecture website and could be considered as a cyber attack. Use reasonable intervals to avoid this.

## Run with Docker

Run the app using Docker:

```bash
docker compose up --build
```

## Run without Docker

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate the virtual environment:

- On Windows:

```bash
venv\Scripts\activate
```

- On macOS/Linux:

```bash
source venv/bin/activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Run the application:

```bash
python app.py
```

**Note**: Setting the frequency of appointment checking too high may result in excessive load on the Rennes prefecture website and could be considered as a cyber attack. Use reasonable intervals to avoid this.
