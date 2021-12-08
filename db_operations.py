"""This Module stores and manages the database collection for the weather.sqlite DB."""

import logging
import sqlite3
from dateutil import parser
from pubsub import pub

class DBCM():
    """Context manager."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self, dbname:str):
        """Intializes an instance of the DBCM class."""

        try:
            self.dbname = dbname
            self.connection = None
            self.cursor = None

        except Exception as error:
            self.logger.error("DBCM:init:%s", error)

    def __enter__(self):
        """Connects to and opens the DB for changes."""

        try:
            self.connection = sqlite3.connect(self.dbname)
            self.cursor = self.connection.cursor()
            return self.cursor

        except Exception as error:
            self.logger.error("DBCM:enter:%s", error)

    def __exit__(self, exc_type, exc_value, exc_trace):
        """Closes the connection."""

        try:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()

        except Exception as error:
            self.logger.error("DBCM:exit:%s", error)

class DBOperations():
    """Handles the databases operations."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self):
        """Intializes the DBOperations class."""
        self.insert_counter = 0

    def intialize_db(self):
        """Intializes the database."""

        try:
            with DBCM("weather.sqlite") as conn:
                conn.execute("""create table if not exists weather
                            (id integer primary key autoincrement not null,
                            sample_date text,
                            location text,
                            min_temp real,
                            max_temp real,
                            avg_temp real);""")

        except Exception as error:
            self.logger.error("DBOps:init:%s", error)

    def fetch_data_year(self, start_year:str, end_year:str) -> dict:
        """Fetches the average temperatures between and including the given year range."""

        try:
            monthly_data = {1:[], 2:[], 3:[], 4:[], 5:[],
                            6:[], 7:[], 8:[], 9:[], 10:[], 11:[], 12:[]}

            date = parser.parse(f'{start_year}-01-01')

            while date.year <= int(end_year):

                try:
                    sql = ("""SELECT sample_date, avg_temp
                            FROM weather
                            WHERE date(sample_date) LIKE ?||'%'
                            ORDER BY sample_date;""")

                    value = (date.year,)

                    with DBCM("weather.sqlite") as conn:
                        for row in conn.execute(sql, value):
                            month = parser.parse(row[0]).month

                            #Removes 'M' characters from data.
                            if type(row[1]) != str:
                                monthly_data[month].append(row[1])

                    date = date.replace(year=date.year + 1)

                except Exception as error:
                    self.logger.error("DBOps:fetch_year loop 1:%s", error)

            return monthly_data

        except Exception as error:
            self.logger.error("DBOps:fetch_year:%s", error)

    def fetch_data_month(self, month:str, year:str) -> dict:
        """Fetches the average temperatures for the given month of the given year."""

        try:
            temps = {}

            sql = ("""SELECT sample_date, avg_temp
                        FROM weather
                        WHERE date(sample_date) LIKE ?||'-'||?||'%'
                        ORDER BY sample_date;""")

            value = (year, month)

            with DBCM("weather.sqlite") as conn:
                for row in conn.execute(sql, value):
                    temps[row[0]] = row[1]

        except Exception as error:
            self.logger.error("DBOps:fetch_month:%s", error)

        return temps

    def save_data(self, data:dict):
        """Saves distinct data to the database."""

        try:
            dates = self.get_db_dates()

            #Only inserts data if the date isnt already in the database.
            for key, value in data.items():
                try:
                    if key not in dates:

                        sql = ("""insert into weather
                            (sample_date, max_temp, min_temp, avg_temp, location)
                            values(?, ?, ?, ?, ?);""")

                        data[key]['location'] = 'Winnipeg, MB'
                        value = (key, value['Max'], value['Min'], value['Mean'], value['location'])

                        with DBCM("weather.sqlite") as conn:
                            conn.execute(sql, value)

                    else:
                        sql = ("""UPDATE weather
                                SET max_temp = ?,
                                    min_temp = ?,
                                    avg_temp = ?,
                                    location = ?
                                WHERE sample_date = ?;""")

                        data[key]['location'] = 'Winnipeg, MB'
                        value = (value['Max'], value['Min'], value['Mean'], value['location'], key)

                        with DBCM("weather.sqlite") as conn:
                            conn.execute(sql, value)
                    
                    self.insert_counter += 1
                    pub.sendMessage('load', counter=self.insert_counter)

                except Exception as error:
                    self.logger.error("DBOps:save loop 1:%s", error)

            pub.sendMessage('complete')

        except Exception as error:
            self.logger.error("DBOps:save:%s", error)

    def purge_data(self):
        """Deletes all data from the DB."""

        try:
            sql = """DROP TABLE weather;"""

            with DBCM("weather.sqlite") as conn:
                conn.execute(sql)

        except Exception as error:
            self.logger.error("DBOps:purge:%s", error)

    def get_db_dates(self) -> list:
        """Grabs all the dates from the database."""

        try:
            dates = []
            sql = ("""SELECT sample_date
                        FROM weather
                        ORDER BY sample_date;""")

            with DBCM("weather.sqlite") as conn:
                for row in conn.execute(sql):
                    dates.append(row[0])

            return dates

        except Exception as error:
            self.logger.error("DBOps:get_dates:%s", error)