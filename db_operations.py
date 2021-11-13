from scrape_weather import WeatherScraper
import sqlite3

class DBOperations():
    
    def __init__(self, dbname:str):
        self.dbname = dbname
        self.connection = None

    def Intialize_db(self):
        self.connection = sqlite3.connect(self.dbname)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""create table if not exists weather
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
            self.cursor.execute(sql, value)

    def fetch_data(self, date:str):

        sql = ("""SELECT *
                    FROM weather
                    WHERE date(sample_date) = ?;""")

        value = (date,)
                    
        for row in self.cursor.execute(sql, value):
            return(row)

    def save_data(self):

        sql = """DELETE FROM weather
                    WHERE id NOT IN
                    (
                        SELECT MAX(id)
                        FROM weather
                        GROUP BY sample_date, min_temp, max_temp, avg_temp, location 
                    );"""

        self.cursor.execute(sql)

        self.connection.commit()

    def purge_data(self):

        sql = """DROP TABLE weather;"""

        self.cursor.execute(sql)

class DBCM:
    """Context manager."""

    def __init__(self, filename, mode):
        """Intializes an instance of the OpenFile class with the specified filename and mode."""
        self.filename = filename
        self.mode = mode
        self.filehandle = None
    
    def __enter__(self):
        """Connects to and opens the file for changes."""
        self.filehandle = open(self.filename, self.mode)
        return self.filehandle
    
    def __exit__(self, exc_type, exc_value, exc_trace):
        """Closes the connection to the file and commits the changes."""
        self.filehandle.close()


if __name__ == "__main__":

    test = DBOperations('WeatherData')
    weatherScrape = WeatherScraper()


    test.Intialize_db()
    test.insert_data(weatherScrape.get_data())
    test.save_data()

    #test.purge_data()