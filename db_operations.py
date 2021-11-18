"""This Module stores and manages the database collection for the weather.sqlite DB."""

from datetime import datetime
import sqlite3
from dateutil import parser
from scrape_weather import WeatherScraper

class DBCM():
    """Context manager."""

    def __init__(self, dbname:str):
        """Intializes an instance of the DBCM class."""
        self.dbname = dbname
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Connects to and opens the DB for changes."""
        self.connection = sqlite3.connect(self.dbname)
        self.cursor = self.connection.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_value, exc_trace):
        """Closes the connection."""
        self.connection.commit()
        self.cursor.close()
        self.connection.close()

class DBOperations():

    def intialize_db(self):
        """Intializes an instance of the DBOperations class."""

        with DBCM("weather.sqlite") as c:
            c.execute("""create table if not exists weather
                        (id integer primary key autoincrement not null,
                        sample_date text,
                        location text,
                        min_temp real,
                        max_temp real,
                        avg_temp real);""")

    def fetch_data_year(self, start_year:str, end_year:str) -> dict:
        """Fetches the average temperatures between and including the given year range."""

        monthly_data = {1:[], 2:[], 3:[], 4:[], 5:[], 6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}
        date = parser.parse(f'{start_year}-01-01')

        while date.year <= int(end_year):

            sql = ("""SELECT sample_date, avg_temp
                    FROM weather
                    WHERE date(sample_date) LIKE ?||'%'
                    ORDER BY sample_date;""")

            value = (date.year,)

            with DBCM("weather.sqlite") as c:
                for row in c.execute(sql, value):
                    month = parser.parse(row[0]).month

                    #Removes 'M' characters from data.
                    if type(row[1]) != str:
                        monthly_data[month].append(row[1])

            date = date.replace(year=date.year + 1)

        return monthly_data

    def fetch_data_month(self, month:str, year:str) -> dict:
        """Fetches the average temperatures for the given month of the given year."""

        temps = {}

        sql = ("""SELECT sample_date, avg_temp
                    FROM weather
                    WHERE date(sample_date) LIKE ?||'-'||?||'%'
                    ORDER BY sample_date;""")

        value = (year, month)

        with DBCM("weather.sqlite") as c:
            for row in c.execute(sql, value):
                temps[row[0]] = row[1]

        return temps

    def save_data(self, data:dict):
        """Saves distinct data to the database."""

        dates = self.get_db_dates()

        #Only inserts data if the date isnt already in the database.
        for k, v in data.items():
            if k not in dates:

                sql = ("""insert into weather
                    (sample_date, max_temp, min_temp, avg_temp, location)
                    values(?, ?, ?, ?, ?);""")

                data[k]['location'] = 'Winnipeg, MB'
                value = (k, v['Max'], v['Min'], v['Mean'], v['location'])

                with DBCM("weather.sqlite") as c:
                    c.execute(sql, value)

            else:
                sql = ("""UPDATE weather
                        SET max_temp = ?,
                            min_temp = ?,
                            avg_temp = ?,
                            location = ?
                        WHERE sample_date = ?;""")

                data[k]['location'] = 'Winnipeg, MB'
                value = (v['Max'], v['Min'], v['Mean'], v['location'], k)

                with DBCM("weather.sqlite") as c:
                    c.execute(sql, value)

    def purge_data(self):
        """Deletes all data from the DB."""

        sql = """DROP TABLE weather;"""

        with DBCM("weather.sqlite") as c:
            c.execute(sql)

    def update(self):
        """Updates the database."""

        today = datetime.now().date()
        dates = self.get_db_dates()
        startdate = parser.parse(dates[-1]).date()

        if today not in dates:
            data = WeatherScraper().update_scrape(startdate)

        self.save_data(data)

    def get_db_dates(self) -> list:
        """Grabs all the dates from the database."""

        dates = []
        sql = ("""SELECT sample_date
                    FROM weather
                    ORDER BY sample_date;""")

        with DBCM("weather.sqlite") as c:
            for row in c.execute(sql):
                dates.append(row[0])

        return dates

#Test Program.
if __name__ == "__main__":

    test = DBOperations()
    weatherScrape = WeatherScraper()
    test.intialize_db()

    #This shouldnt Update the DB.
    #test.save_data({'1997-11-30':{'Min': -12.8, 'Max': -3.5, 'Mean': -8.2}})
    test.update()
    #test.save_data(weatherScrape.get_data())
    #print(test.fetch_data_year('2020', '2020'))
    #print(test.fetch_data_month('01','2020'))
