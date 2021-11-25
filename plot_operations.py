"""This Module displays a box graph and a line graph."""

import logging
import matplotlib.pyplot as plt
from db_operations import DBOperations

class PlotOperations():
    """Creates graphs with the mean temperature of the user provided dates."""

    logger = logging.getLogger("main." + __name__)

    def create_box_plot(self, start_year:str, end_year:str):
        """Creates a box plot based on the data provided by the user."""

        try:
            data = DBOperations().fetch_data_year(start_year, end_year)
            
            hitest = list(data.values())

            plt.boxplot(hitest)
            plt.title(f'Monthly temperature distribution for: {start_year} to {end_year}')
            plt.ylabel('Temperature (Celcius)')
            plt.xlabel('Month')
            plt.show()

        except Exception as error:
            self.logger.error("PlotOps:boxplot:%s", error)

    def create_line_plot(self, month:str, year:str):
        """Creates a line plot based on the data provided by the user."""

        try:
            data = DBOperations().fetch_data_month(month, year)

            dates = list(data.keys())
            temps = list(data.values())

            plt.plot(dates, temps)
            plt.title('Daily Avg Temperatures')
            plt.ylabel('Avg Daily Temp')
            plt.xlabel('Days of Month')
            plt.xticks(rotation = 70, horizontalalignment = 'right', rotation_mode = 'anchor')
            plt.show()

        except Exception as error:
            self.logger.error("PlotOps:lineplot:%s", error)

#Test Program.
if __name__ == "__main__":
    test = PlotOperations()
    test.create_box_plot('2000', '2017')
    test.create_line_plot('01', '2020')
