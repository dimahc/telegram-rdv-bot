from typing import Any

from bs4 import BeautifulSoup
from pyppeteer import launch

import config


class Scraper:
    async def scrape(self):
        """
        Launches a headless browser, navigates to the configured URL, and retrieves the page content.
        Returns the HTML content of the page.
        """
        browser = await launch(
            {
                "headless": True,
                "executablePath": config.CHROMIUM_PATH,
                "args": ["--no-sandbox", "--disable-setuid-sandbox"],
            }
        )
        page = await browser.newPage()
        await page.goto(config.URL)

        # Wait for the calendar to be visible
        await page.waitForSelector(".rdv-calendar.calendar", {"visible": True})

        # Check for user error messages
        error_msg = await page.evaluate(
            'document.querySelector(".user-msg.error")?.textContent'
        )
        if error_msg:
            print("User error message:", error_msg)
            await browser.close()
            return ""

        # Wait for the day columns to be visible
        await page.waitForSelector("div.day-column", {"visible": True})

        # Get the page content
        html_content = await page.content()
        await browser.close()
        return html_content

    def extract_appointments(self, html_content: str):
        """
        Parses the HTML content to extract available appointment slots.
        Returns a list of available slots with date, time, and location.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        day_columns = soup.find_all("div", class_="day-column ng-star-inserted")
        available_slots: list[Any] = []
        for day_column in day_columns:
            day_header = day_column.find_previous("div", class_="day-header")
            day_date = day_header.find("div", class_="header-date").text.strip()
            slots = day_column.find_all("li", class_="time-slot")
            for slot in slots:
                slot_time = slot.find("span", class_="hour").text.strip()
                slot_location = slot.find("div", class_="site-name").text.strip()
                appointment = {
                    "date": day_date,
                    "time": slot_time,
                    "location": slot_location,
                }
                available_slots.append(appointment)

        print(available_slots)
        return available_slots
