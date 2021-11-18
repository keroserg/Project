"""Creates and manages the UI for the weather processing app."""

import wx
import wx.core
from dateutil import parser
from db_operations import DBOperations
from scrape_weather import WeatherScraper
from plot_operations import PlotOperations

class App(wx.App):
    """Creates the app and intializes the frame."""

    def __init__(self):
        """Intializes an instance of the App class."""

        super().__init__(clearSigInt=True)
        self.init_frame()

    def init_frame(self):
        """Intializes and displays a frame with specific settings."""

        size = wx.DisplaySize()
        frame = Frame(parent=None, title='Weather Processor', pos=(0, 0))

        frame.SetSize(550, 350)
        winsize = frame.GetSize()
        frame.SetPosition((int(size[0]/2 - winsize[0]/2), int(size[1]/2 - winsize[1]/2)))

        frame.SetIcon(wx.Icon("images/icon.png"))

        frame.Show()

class Frame(wx.Frame):
    """Creates the frame and intializes the panel."""

    def __init__(self, parent, title, pos):
        """Intializes an instance of the Frame class."""

        super().__init__(parent=parent, title=title, pos=pos)
        self.on_init()

    def on_init(self):
        """Intializes a panel."""

        panel = WeatherProcessor(parent=self)

class WeatherProcessor(wx.Panel):
    """Creates the users controls and handles related events."""

    def __init__(self, parent):
        """Intializes an instance of the WeatherProcessor class with the given settings."""

        super().__init__(parent=parent)

        wx.StaticText(parent=self, label = "Choose a method to fetch data with:", pos = (20, 30))
        wx.StaticText(parent=self, label = "Choose a type of graph:", pos = (320, 30))
        self.starttext = wx.StaticText(parent=self, label = "Starting Year:", pos = (300, 160))
        self.endtext = wx.StaticText(parent=self, label = "Ending Year:", pos = (400, 160))
        self.monthtext = wx.StaticText(parent=self, label = "Month:", pos = (400, 160))
        self.yeartext = wx.StaticText(parent=self, label = "Year:", pos = (300, 160))

        dlbutton = wx.Button(parent=self, label = "Download weather data", pos = (20, 250))
        plotbutton = wx.Button(parent=self, label = "Create Plot", pos = (350, 250))

        self.rad_update = wx.RadioButton(parent=self,
                                         label = "Download new weather data", pos = (20, 80))

        self.rad_update.SetValue(True)
        self.rad_new = wx.RadioButton(parent=self,
                                    label = "Download all weather data", pos = (20, 110))

        self.rad_box = wx.RadioButton(parent=self, label = "Box Plot (Monthly)", pos = (320, 80))
        self.rad_line = wx.RadioButton(parent=self, label = "Line Plot (Daily)", pos = (320, 110))

        months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
        years = []

        for row in DBOperations().get_db_dates():
            temp = str(parser.parse(row).year)
            if temp not in years:
                years.append(temp)

        self.monthcombo = wx.ComboBox(parent=self, pos=(400, 180), size=(80, 100),
                                        choices= months, style=wx.CB_DROPDOWN)

        self.monthcombo.SetSelection(0)
        self.startyearbox = wx.ComboBox(parent=self, pos=(300, 180), size=(80, 100),
                                        choices= years, style=wx.CB_DROPDOWN)

        self.startyearbox.SetSelection(0)
        self.endyearbox = wx.ComboBox(parent=self, pos=(400, 180), size=(80, 100),
                                        choices= years, style=wx.CB_DROPDOWN)

        self.endyearbox.SetSelection(0)

        self.monthcombo.Hide()
        self.startyearbox.Hide()
        self.endyearbox.Hide()
        self.starttext.Hide()
        self.endtext.Hide()
        self.monthtext.Hide()
        self.yeartext.Hide()

        dlbutton.Bind(event=wx.EVT_BUTTON, handler=self.download_submit)
        plotbutton.Bind(event=wx.EVT_BUTTON, handler=self.plot_submit)
        self.rad_box.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)
        self.rad_line.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)
        self.rad_new.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)
        self.rad_update.Bind(event=wx.EVT_RADIOBUTTON, handler=self.show_boxes)

    def download_submit(self, event):
        """Handles the click event for the download button."""

        if self.rad_update.GetValue():
            DBOperations().update()

        if self.rad_new.GetValue():
            scraper = WeatherScraper()
            DBOperations().save_data(scraper.get_data())

    def plot_submit(self, event):
        """Handles the click event for the plot button."""

        if self.rad_line.GetValue() and self.monthcombo.GetValue() != '' and self.startyearbox.GetValue() != '':
            month = self.monthcombo.GetValue()
            year = self.startyearbox.GetValue()
            PlotOperations().create_line_plot(month, year)

        if self.rad_box.GetValue() and self.endyearbox.GetValue() != '' and self.startyearbox.GetValue() != '' and not self.endyearbox.GetValue() < self.startyearbox.GetValue():
            start = self.startyearbox.GetValue()
            end = self.endyearbox.GetValue()
            PlotOperations().create_box_plot(start, end)

    def show_boxes(self, event):
        """Handles the checked events for the radio boxes."""
        if self.rad_box.GetValue():
            self.startyearbox.Show()
            self.endyearbox.Show()
            self.monthcombo.Hide()
            self.monthtext.Hide()
            self.starttext.Show()
            self.endtext.Show()
            self.yeartext.Hide()

        if self.rad_line.GetValue():
            self.startyearbox.Show()
            self.starttext.Hide()
            self.monthcombo.Show()
            self.endyearbox.Hide()
            self.endtext.Hide()
            self.monthtext.Show()
            self.yeartext.Show()

        if not self.rad_line.GetValue() and not self.rad_box.GetValue():
            self.monthcombo.Hide()
            self.startyearbox.Hide()
            self.endyearbox.Hide()
            self.starttext.Hide()
            self.endtext.Hide()
            self.monthtext.Hide()
            self.yeartext.Hide()

if __name__ == "__main__":
    app = App()
    app.MainLoop()
