from html.parser import HTMLParser
import urllib.request
from datetime import datetime

class WeatherScraper(HTMLParser):

    def __init__(self):
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
        if tag == "tbody":
            self.tbody = True
        
        if tag == "tr" and self.tbody == True:
            self.tr = True

        if tag == "td" and self.tr == True:
            self.counter += 1
            self.td = True

        if tag == "abbr" and self.tr == True:
           self.rowDate = str(datetime.strptime(attrs[0][1], "%B %d, %Y").date())

        if len(attrs) == 2:
            if attrs[1][1] == "previous disabled":
                self.lastPage = True

    def handle_endtag(self, tag):
        
        if tag == "td":
            self.td = False
        
        if tag == "tr":
            self.counter = 0
            self.tr = False
        
    def handle_data(self, data):

        if data == "Sum":
            self.tbody = False
    
        if self.td == True and self.counter <= 3 and self.tbody == True:
            keys = ['Max', 'Min', 'Mean']
            self.daily_temps[keys[self.counter - 1]] = data

        if self.counter == 3:
            self.weather[self.rowDate] = self.daily_temps
            self.daily_temps = self.daily_temps.copy()

if __name__ == "__main__":

    weatherScrape = WeatherScraper()

    today  = datetime.now()

    while (weatherScrape.lastPage == False):

        Url = (f'https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID=27174&timeframe=2&StartYear=1840&EndYear=2018&Day={today.day}&Year={today.year}&Month={today.month}#')

        if today.month == 1:
            today = today.replace(month=12)
            today = today.replace(year=today.year-1)
        
        else:
            today = today.replace(month=today.month-1)
        
        with urllib.request.urlopen(Url) as response:
            html = str(response.read())

        weatherScrape.feed(html)

        for k, v in weatherScrape.weather.items():
            print(k, v)
