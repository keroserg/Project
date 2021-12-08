"""This Module scrapes weather data for max, min and mean."""

from html.parser import HTMLParser
import logging
import urllib.request
from pubsub import pub
from datetime import datetime

class WeatherScraper(HTMLParser):
    """Weather data HTML scraper."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self):
        """Intializes an instance of the WeatherScraper class."""
        try:
            super().__init__()
            self.tbody = False
            self.tr = False
            self.td = False
            self.counter = 0
            self.daily_temps = {}
            self.weather = {}
            self.row_date = ""
            self.last_page = False
            self.month_counter = 0

        except Exception as error:
            self.logger.error("scrape:init:%s", error)

    def handle_starttag(self, tag, attrs):
        """Handles the starttag event."""

        try:
            if tag == "tbody":
                self.tbody = True

            if tag == "tr" and self.tbody is True:
                self.tr = True

            if tag == "td" and self.tr is True:
                self.counter += 1
                self.td = True

            #Translates abbr tag into the desired date format.
            if tag == "abbr" and self.tr is True:
                self.row_date = str(datetime.strptime(attrs[0][1], "%B %d, %Y").date())

            #Detects last page.
            if len(attrs) == 2:
                if attrs[1][1] == "previous disabled":
                    self.last_page = True

        except Exception as error:
            self.logger.error("scrape:starttag:%s", error)

    def handle_endtag(self, tag):
        """Handles the endtag event."""

        try:
            if tag == "td":
                self.td = False

            if tag == "tr":
                self.counter = 0
                self.tr = False

        except Exception as error:
            self.logger.error("scrape:endtag:%s", error)

    def handle_data(self, data):
        """Handles the data event."""

        try:
            if data == "Sum":
                self.tbody = False

            #Populates daily_temps dict.
            if self.td is True and self.counter <= 3 and self.tbody is True:
                keys = ['Max', 'Min', 'Mean']
                self.daily_temps[keys[self.counter - 1]] = data

            #Populates weather dict.
            if self.counter == 3:
                self.weather[self.row_date] = self.daily_temps
                self.daily_temps = self.daily_temps.copy()

        except Exception as error:
            self.logger.error("scrape:data:%s", error)

    def get_data(self) -> dict:
        """Scrapes each month and year, returns a dictonary containing the weather data."""

        try:
            today  = datetime.now()

            while self.last_page is False:

                try:
                    url = (f'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day={today.day}&Year={today.year}&Month={today.month}#')

                    if today.month == 1:
                        today = today.replace(month=12)
                        today = today.replace(year=today.year-1)

                    else:
                        today = today.replace(month=today.month-1)

                    with urllib.request.urlopen(url) as response:
                        html = str(response.read())

                    self.month_counter += 1

                    self.feed(html)

                    pub.sendMessage('load', counter=self.month_counter)

                except Exception as error:
                    self.logger.error("scrape:get_data loop 1:%s", error)

            return self.weather

        except Exception as error:
            self.logger.error("scrape:get_data:%s", error)

    def update_scrape(self, enddate:datetime) -> dict:
        """Only scrapes the data till it reaches the provided end month and year."""

        try:
            today = datetime.now().date()
            completed = False

            while not completed:

                try:
                    if(enddate.month == today.month) and (enddate.year == today.year):
                        completed = True

                    url = (f'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day={today.day}&Year={today.year}&Month={today.month}#')

                    if today.month == 1:
                        today = today.replace(month=12)
                        today = today.replace(year=today.year-1)

                    else:
                        today = today.replace(month=today.month-1)

                    with urllib.request.urlopen(url) as response:
                        html = str(response.read())

                    self.month_counter += 1
                    
                    self.feed(html)

                    pub.sendMessage('load', counter=self.month_counter)

                except Exception as error:
                    self.logger.error("scrape:update loop 1:%s", error)

            return self.weather

        except Exception as error:
            self.logger.error("scrape:update:%s", error)

#Test Program.
if __name__ == "__main__":
    test = WeatherScraper().get_data()
    for k, v in test.items():
        print(k, v)
