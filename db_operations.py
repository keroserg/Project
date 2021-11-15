from scrape_weather import WeatherScraper
import sqlite3

class DBCM:
    """Context manager."""

    def __init__(self, dbname:str):
        """Intializes an instance of the DBCM class."""
        self.dbname = dbname

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

    def Intialize_db(self):
        """Intializes an instance of the DBOperations class."""

        with DBCM("weather.sqlite") as c:
            c.execute("""create table if not exists weather
                        (id integer primary key autoincrement not null,
                        sample_date text,
                        location text,
                        min_temp real,
                        max_temp real,
                        avg_temp real);""")
    
    
    def fetch_data(self, date:str) -> tuple:
        """Fetches the databases data for the given date."""

        sql = ("""SELECT *
                    FROM weather
                    WHERE date(sample_date) = ?;""")

        value = (date,)

        with DBCM("weather.sqlite") as c:
            for row in c.execute(sql, value):
                return(row)

    def save_data(self, data:dict):
        """Saves distinct data to the database."""
        
        dates = []
        sql = ("""SELECT sample_date
                    FROM weather""")

        with DBCM("weather.sqlite") as c:
            for row in c.execute(sql):
                dates.append(row[0])

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

    def purge_data(self):
        """Deletes all data from the DB."""

        sql = """DROP TABLE weather;"""

        with DBCM("weather.sqlite") as c:
            c.execute(sql)

#Test Program.
if __name__ == "__main__":

    test = DBOperations()
    weatherScrape = WeatherScraper()
    test.Intialize_db()

    #This shouldnt Update the DB.
    test.save_data({'1996-10-31':{'Min': -12.8, 'Max': -3.5, 'Mean': -8.2}})
    print(test.fetch_data('2001-10-19'))

    #test.purge_data()