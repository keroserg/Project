"""This Module scrapes weather data for max, min and mean."""

from html.parser import HTMLParser
import urllib.request
from datetime import datetime

class WeatherScraper(HTMLParser):
    """Weather data HTML scraper."""

    def __init__(self):
        """Intializes an instance of the WeatherScraper class."""

        super().__init__()
        self.tbody = False
        self.tr = False
        self.td = False
        self.counter = 0
        self.daily_temps = {}
        self.weather = {}
        self.rowDate = ""
        self.lastPage = False
        
    def handle_starttag(self, tag, attrs):
        """Handles the starttag event."""

        if tag == "tbody":
            self.tbody = True
        
        if tag == "tr" and self.tbody == True:
            self.tr = True

        if tag == "td" and self.tr == True:
            self.counter += 1
            self.td = True
        
        #Translates abbr tag into the desired date format.
        if tag == "abbr" and self.tr == True:
           self.rowDate = str(datetime.strptime(attrs[0][1], "%B %d, %Y").date())

        #Detects last page.
        if len(attrs) == 2:
            if attrs[1][1] == "previous disabled":
                self.lastPage = True

    def handle_endtag(self, tag):
        """Handles the endtag event."""
        
        if tag == "td":
            self.td = False
        
        if tag == "tr":
            self.counter = 0
            self.tr = False
        
    def handle_data(self, data):
        """Handles the data event."""

        if data == "Sum":
            self.tbody = False
        
        #Populates daily_temps dict.
        if self.td == True and self.counter <= 3 and self.tbody == True:
            keys = ['Max', 'Min', 'Mean']
            self.daily_temps[keys[self.counter - 1]] = data

        #Populates weather dict.
        if self.counter == 3:
            self.weather[self.rowDate] = self.daily_temps
            self.daily_temps = self.daily_temps.copy()

    def get_data(self):
        #Figures out the starting URL and then updates the URL back as far as possible.

        today  = datetime.now()

        while (self.lastPage == False):

            Url = (f'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day={today.day}&Year={today.year}&Month={today.month}#')

            if today.month == 1:
                today = today.replace(month=12)
                today = today.replace(year=today.year-1)
            
            else:
                today = today.replace(month=today.month-1)
            
            with urllib.request.urlopen(Url) as response:
                html = str(response.read())

            self.feed(html)

        return self.weather

if __name__ == "__main__":
    test = WeatherScraper().get_data()
    for k, v in test.items:
        print(k, v)
    
