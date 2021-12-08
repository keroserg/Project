"""Creates and manages the UI for the weather processing app."""

import logging
import wx
import wx.core
from dateutil import parser
from datetime import date, datetime
from pubsub import pub
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations
import error_logger

class App(wx.App):
    """Creates the app and intializes the frame."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self):
        """Intializes an instance of the App class."""

        try:
            super().__init__(clearSigInt=True)
            self.init_frame()
        except Exception as error:
            self.logger.error("App:init:%s", error)

    def init_frame(self):
        """Intializes and displays a frame with specific settings."""

        try:
            size = wx.DisplaySize()
            frame = Frame(parent=None, title='Weather Processor', pos=(0, 0), style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)

            frame.SetSize(550, 350)
            winsize = frame.GetSize()
            frame.SetPosition((int(size[0]/2 - winsize[0]/2), int(size[1]/2 - winsize[1]/2)))

            frame.SetIcon(wx.Icon("images/icon.png"))

            frame.Show()
        except Exception as error:
            self.logger.error("App:init_frame:%s", error)

class Frame(wx.Frame):
    """Creates the frame and intializes the panel."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self, parent, title, pos, style):
        """Intializes an instance of the Frame class."""

        try:
            super().__init__(parent=parent, title=title, pos=pos, style=style)
            self.on_init()

        except Exception as error:
            self.logger.error("Frame:init:%s", error)

    def on_init(self):
        """Intializes a panel."""

        try:
            panel = WeatherProcessor(parent=self)

        except Exception as error:
            self.logger.error("Frame:on_init:%s", error)

class WeatherProcessor(wx.Panel):
    """Creates the users controls and handles related events."""

    logger = logging.getLogger("main." + __name__)

    def __init__(self, parent):
        """Intializes an instance of the WeatherProcessor class with the given settings."""

        try:
            super().__init__(parent=parent)

            self.error_flag = False
            self.flag = False
            self.load_range = 0

            DBOperations().intialize_db()

            #Creates the text labels.
            wx.StaticText(parent=self, label = "Choose a method to fetch data with:", pos = (20, 30))
            self.graphtext = wx.StaticText(parent=self, label = "Choose a type of graph:", pos = (320, 30))
            self.starttext = wx.StaticText(parent=self, label = "Starting Year:", pos = (300, 160))
            self.endtext = wx.StaticText(parent=self, label = "Ending Year:", pos = (400, 160))
            self.monthtext = wx.StaticText(parent=self, label = "Month:", pos = (400, 160))
            self.yeartext = wx.StaticText(parent=self, label = "Year:", pos = (300, 160))

            self.range_error = wx.StaticText(parent=self, label = "Starting year cannot be past ending year", pos = (280, 220))
            self.range_error.SetForegroundColour(wx.RED)

            self.range_error.Hide()

            #Creates the buttons.
            dlbutton = wx.Button(parent=self, label = "Download weather data", pos = (20, 250))
            self.plotbutton = wx.Button(parent=self, label = "Create Plot", pos = (350, 250))
            self.rad_update = wx.RadioButton(parent=self, label = "Download new weather data", pos = (20, 80))
            self.rad_update.SetValue(True)
            self.rad_new = wx.RadioButton(parent=self, label = "Download all weather data", pos = (20, 110))

            #Creating the bitmap buttons.
            line_image = wx.Image("images/line.png", wx.BITMAP_TYPE_ANY)
            box_image = wx.Image("images/box.png", wx.BITMAP_TYPE_ANY)
            line_image.Rescale(75,75)
            box_image.Rescale(75,75)
            bit_box = box_image.ConvertToBitmap()
            bit_line = line_image.ConvertToBitmap()

            self.boxbutton = wx.BitmapButton(self, -1, bit_box, pos=(400, 75), size=(80,80))
            self.linebutton = wx.BitmapButton(self, -1, bit_line, pos=(300, 75), size=(80,80))

            months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
            self.years = []

            #Figures out the number of years the comboboxes should display.
            for row in DBOperations().get_db_dates():
                try:
                    temp = str(parser.parse(row).year)
                    if temp not in self.years:
                        self.years.append(temp)

                except Exception as error:
                    self.logger.error("WeatherProcessor:init loop 1:%s", error)

            #Hide these fields on first time run.
            if not self.years:
                self.rad_update.Hide()
                self.boxbutton.Hide()
                self.linebutton.Hide()
                self.graphtext.Hide()
                self.plotbutton.Hide()

            #Creating the comboboxes.
            self.monthcombo = wx.ComboBox(parent=self, pos=(400, 180), size=(80, 100), choices= months, style=wx.CB_READONLY)

            self.monthcombo.SetSelection(0)
            self.startyearbox = wx.ComboBox(parent=self, pos=(300, 180), size=(80, 100), choices= self.years, style=wx.CB_READONLY)

            self.startyearbox.SetSelection(0)
            self.endyearbox = wx.ComboBox(parent=self, pos=(400, 180), size=(80, 100), choices= self.years, style=wx.CB_READONLY)

            self.endyearbox.SetSelection(0)

            self.monthcombo.Hide()
            self.startyearbox.Hide()
            self.endyearbox.Hide()
            self.starttext.Hide()
            self.endtext.Hide()
            self.monthtext.Hide()
            self.yeartext.Hide()

            #Subscriptions.
            pub.subscribe(self.load_listener, 'load')
            pub.subscribe(self.complete_listener, 'complete')
            dlbutton.Bind(event=wx.EVT_BUTTON, handler=self.download_submit)
            self.plotbutton.Bind(event=wx.EVT_BUTTON, handler=self.plot_submit)
            self.boxbutton.Bind(event=wx.EVT_BUTTON, handler=self.show_boxes)
            self.linebutton.Bind(event=wx.EVT_BUTTON, handler=self.show_boxes)
            self.rad_new.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)
            self.rad_update.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)

        except Exception as error:
            self.logger.error("WeatherProcessor:init:%s", error)
 
    def update(self):
        """Updates the database."""

        try:
            today = datetime.now().date()
            dates = DBOperations().get_db_dates()
            startdate = parser.parse(dates[-1]).date()

            if today not in dates:
                data = WeatherScraper().update_scrape(startdate)

            DBOperations().save_data(data)

        except Exception as error:
            self.logger.error("weather_processor:update:%s", error)

    def refresh(self):
        """Reloads the combo boxes."""

        try:
            self.flag = False
            self.startyearbox.Clear()
            self.endyearbox.Clear()

            for row in DBOperations().get_db_dates():
                try:
                    temp = str(parser.parse(row).year)
                    if temp not in self.years:
                        self.years.append(temp)

                except Exception as error:
                    self.logger.error("WeatherProcessor:load loop 1:%s", error)

            self.startyearbox.AppendItems(self.years)
            self.endyearbox.AppendItems(self.years)
            self.endyearbox.SetSelection(0)
            self.startyearbox.SetSelection(0)

        except Exception as error:
            self.logger.error("WeatherProcessor:load:%s", error)

    def download_submit(self, event):
        """Handles the click event for the download button."""

        try:
            today = date.today()
            total_months = (today.year - 1995) * 12 - 9 - (12 - today.month)

            if self.years:
                dblast_month = parser.parse(DBOperations().get_db_dates()[-1])
                update_year = today.year - int(self.years[-1])
                update_months = today.month - dblast_month.month
                update_bar_range = update_year * 12 + update_months + 1

            if self.rad_update.GetValue():
                self.loading_bar()
                load_bar.SetRange(update_bar_range)
                self.update()
                self.refresh()

            if self.rad_new.GetValue():
                scraper = WeatherScraper()
                self.loading_bar()
                load_bar.SetRange(total_months)
                DBOperations().save_data(scraper.get_data())
                self.refresh()
                self.rad_update.Show()
                self.graphtext.Show()
                self.linebutton.Show()
                self.boxbutton.Show()
                self.plotbutton.Show()

        except Exception as error:
            self.logger.error("WeatherProcessor:download_submit:%s", error)

    def loading_bar(self):
        """Creates a global progress dialog control."""
        
        global load_bar
        load_bar = wx.ProgressDialog("Downloading Weather Data", "Retrieving Data", maximum=100, parent=self, 
                        style=wx.PD_APP_MODAL|wx.PD_ESTIMATED_TIME|wx.PD_ELAPSED_TIME)
    
    def load_listener(self, counter):
        """Listener that updates the loadbar"""

        load_bar.Update(counter)
        start_date = date(1996, 10, 1)
        today = date.today()

        if counter == load_bar.GetRange()-1 and self.flag is False:

            self.flag = True
            self.load_range

            self.load_range = today - start_date
            load_bar.Update(0, "Inserting Data.")
            load_bar.SetRange(self.load_range.days)

    def complete_listener(self):
        """Listener that fills the loadbar to prevent the loadbar from possibly getting stuck."""

        load_bar.Update(self.load_range.days)

    def plot_submit(self, event):
        """Handles the click event for the plot button."""

        try:
            self.validate()
            
            if self.error_flag is False:

                self.range_error.Hide()

                if self.monthcombo.IsShown() is True:
                    month = self.monthcombo.GetValue()
                    year = self.startyearbox.GetValue()
                    data = DBOperations().fetch_data_month(month, year)
                    PlotOperations().create_line_plot(month, year, data)

                if self.endyearbox.IsShown() is True:
                    start = self.startyearbox.GetValue()
                    end = self.endyearbox.GetValue()
                    data = DBOperations().fetch_data_year(start, end)
                    PlotOperations().create_box_plot(start, end, data)

        except Exception as error:
            self.logger.error("WeatherProcessor:plot_submit:%s", error)

    def validate(self):
        """Validates the inputs."""
        
        try:
            self.error_flag = False

            if self.startyearbox.Value > self.endyearbox.Value and self.endyearbox.IsShown() is True:
                self.error_flag = True
                self.range_error.Show()

        except logging.exception as error:
            self.logger.error("WeatherProcessor:validate:%s", error)


    def show_boxes(self, event):
        """Handles the checked events for the radio boxes."""
        
        try:
            if self.boxbutton.HasFocus():
                self.startyearbox.Show()
                self.endyearbox.Show()
                self.monthcombo.Hide()
                self.monthtext.Hide()
                self.starttext.Show()
                self.endtext.Show()
                self.yeartext.Hide()
                self.endyearbox.SetSelection(0)

            if self.linebutton.HasFocus():
                self.startyearbox.Show()
                self.starttext.Hide()
                self.monthcombo.Show()
                self.endyearbox.Hide()
                self.endtext.Hide()
                self.monthtext.Show()
                self.yeartext.Show()

        except Exception as error:
            self.logger.error("WeatherProcessor:show_boxes:%s", error)

if __name__ == "__main__":
    app = App()
    app.MainLoop()
