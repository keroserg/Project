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
        
        with DBCM("weather.sqlite") as c:
            c.execute("""create table if not exists weather
                        (id integer primary key autoincrement not null,
                        sample_date text,
                        location text,
                        min_temp real,
                        max_temp real,
                        avg_temp real);""")
    
    def insert_data(self, dict:dict):

        sql = ("""insert into weather
            (sample_date, max_temp, min_temp, avg_temp, location)
            values(?, ?, ?, ?, ?);""")

        for k, v in dict.items():
            dict[k]['location'] = 'Winnipeg, MB'
            value = (k, v['Max'], v['Min'], v['Mean'], v['location'])
            
            with DBCM("weather.sqlite") as c:
                c.execute(sql, value)

    def fetch_data(self, date:str):

        sql = ("""SELECT *
                    FROM weather
                    WHERE date(sample_date) = ?;""")

        value = (date,)

        with DBCM("weather.sqlite") as c:
            for row in c.execute(sql, value):
                return(row)

    def save_data(self):

        sql = """DELETE FROM weather
                    WHERE id NOT IN
                    (
                        SELECT MAX(id)
                        FROM weather
                        GROUP BY sample_date, min_temp, max_temp, avg_temp, location 
                    );"""

        with DBCM("weather.sqlite") as c:
            c.execute(sql)

    def purge_data(self):

        sql = """DROP TABLE weather;"""

        with DBCM("weather.sqlite") as c:
            c.execute(sql)

if __name__ == "__main__":

    test = DBOperations()
    weatherScrape = WeatherScraper()


    test.Intialize_db()
    test.insert_data(weatherScrape.get_data())
    test.save_data()