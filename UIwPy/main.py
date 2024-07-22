# Imports
import sys
import os
import time
import datetime as dt
import asyncio

from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QAction
from PyQt5 import QtCore, QtGui, QtWidgets
from QTUI import Ui_MainWindow  # Import the generated UI class

import utils.CGcontacter as CGcontacter
import utils.logger as logger
import utils.settings_manager as settings_manager
import utils.units_manager as units_manager
import utils.plotter as plotter
from PyQt5.QtCore import QTimer
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from PyQt5.QtCore import QTimer
import time
import time


# Globals
LOG_FOLDER_PATH = "./logFiles"
MEASUREMENTS_FOLDER_PATH = "./measurements"
ICONS_FOLDER_PATH = "./icons"

SETTINGS_FILE_PATH = "./utils/settings.json"
UNITS_FILE_PATH = "./utils/units.json"
HELP_PAGE_TEXT_FILE_PATH = "./utils/HelpPageText.txt"

FAVICON_ICON_PATH = ICONS_FOLDER_PATH + "/favicon.ico"
DISCONNECTED_ICON_PATH = ICONS_FOLDER_PATH + "/disconnected.ico"
CONNECTED_ICON_PATH = ICONS_FOLDER_PATH + "/connected.ico"
GREENDOT_ICON_PATH = ICONS_FOLDER_PATH + "/greendot.ico"
REDDOT_ICON_PATH = ICONS_FOLDER_PATH + "/reddot.ico"
HELP_ICON_PATH = ICONS_FOLDER_PATH + "/Help.ico"

SETTINGS_TAB_NAME = "Settings"
LIVE_PLOT_TAB_NAME = "Live-Plot"
HELP_TAB_NAME = "Help"

SETTINGS_TAB_SUBTAB_1_NAME = "Device and Data File"
SETTINGS_TAB_SUBTAB_2_NAME = "Sensors and Units"
SETTINGS_TAB_SUBTAB_3_NAME = "Run Details"

log_obj = logger.logger(f"{LOG_FOLDER_PATH}/{str(dt.datetime.now()).replace(':', '-')}.txt")
json_settings = settings_manager.settings_manager(SETTINGS_FILE_PATH)
json_units = units_manager.units_manager(UNITS_FILE_PATH)


# util functions
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False


# Main
class MainWindow(QMainWindow):
    def __init__(self):
        self.plot_controller = None
        self.IGplotData = False
        self.CG1plotData = False
        self.CG2plotData = False

        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window icon
        self.setWindowIcon(QtGui.QIcon(FAVICON_ICON_PATH))

        # Menu Bar Pages
        file_action_tmp = QAction(SETTINGS_TAB_NAME, self)
        def Home_Page_On():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page1)
        file_action_tmp.triggered.connect(Home_Page_On)
        self.ui.menubar.addAction(file_action_tmp)

        file_action_tmp = QAction(LIVE_PLOT_TAB_NAME, self)
        def Plot_Page_On():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page2)
        file_action_tmp.triggered.connect(Plot_Page_On)
        self.ui.menubar.addAction(file_action_tmp)

        file_action_tmp = QAction(HELP_TAB_NAME, self)
        def Help_Page_On():
            self.ui.stackedWidget.setCurrentWidget(self.ui.page3)
        file_action_tmp.triggered.connect(Help_Page_On)
        self.ui.menubar.addAction(file_action_tmp)

        # Help icons
        self.ui.connectDeviceButton.setIcon(QtGui.QIcon(DISCONNECTED_ICON_PATH))
        self.ui.connectDeviceHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.SaveFilePathHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.maxRuntimeHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.timeLatencyHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.IGplotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG1plotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG2plotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))

        # insert values into ComboBoxes
        pressure_units = json_units.get_pressure_units()
        time_units = json_units.get_time_units()
        self.ui.PlotPressureUnitCombo.insertItems(0, pressure_units[:])
        self.ui.PlotTimeUnitCombo.insertItems(0, time_units[:])

        # insert Help Page content
        with open(HELP_PAGE_TEXT_FILE_PATH, "r") as fp:
            self.ui.helpPageLabel.setText(fp.read())
 
        # settings page tabs names
        self.ui.tabWidget.setTabText(0, SETTINGS_TAB_SUBTAB_1_NAME)
        self.ui.tabWidget.setTabText(1, SETTINGS_TAB_SUBTAB_3_NAME)

        # toolbar
        # hide green-dot
        self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(REDDOT_ICON_PATH))
        self.ui.ToolBarStatusLabel.setText("Status: Disconnected")
        self.ui.ToolBarIGPLabel.setText("IGP: OFF")
        self.ui.ToolBarCG1PLabel.setText("CG1P: OFF")
        self.ui.ToolBarCG2PLabel.setText("CG2P: OFF")

        ########################
        # load settings into fields
        ########################
        ## settings ##
        # tab1 #
        self.ui.DevicePortLineEdit.setText(json_settings.get_settings_attribute("device port"))
        # self.ui.SaveFilePathLineEdit.setText(json_settings.get_settings_attribute("save data to"))
        json_settings.set_settings_attribute("save data to", "")
        # self.ui.SaveFilePathCheckBox.setChecked(json_settings.get_settings_attribute("auto file name") == "True")
        json_settings.set_settings_attribute("auto file name", "False")
        # tab3 #
        tmp = str(json_settings.get_settings_attribute("max runtime"))
        tmp = int(tmp) if is_int(tmp) else 0
        self.ui.MaxRuntimeSpinBox.setValue(tmp)
        tmp = str(json_settings.get_settings_attribute("time latency"))
        tmp = float(tmp) if is_float(tmp) else 0
        self.ui.TimeLatencyDoubleSpinBox.setValue(tmp)
        if json_settings.get_settings_attribute("save log files") == "True":
            self.ui.CreateLogFileCheckBox.setChecked(True)
            log_obj.set_auto_save(True)
        ## live plot ##
        self.ui.PlotPressureUnitCombo.setCurrentText(json_settings.get_live_plot_attribute("pressure unit"))
        self.ui.PlotTimeUnitCombo.setCurrentText(json_settings.get_live_plot_attribute("time unit"))
        self.ui.XAxisLogScaleCheckbox.setChecked(json_settings.get_live_plot_attribute("x axis log scale") == "True")
        self.ui.YAxisLogScaleCheckbox.setChecked(json_settings.get_live_plot_attribute("y axis log scale") == "True")
        self.ui.GriddedCheckBox.setChecked(json_settings.get_live_plot_attribute("gridded") == "True")
        # IG
        self.ui.IGPlotItCheckBox.setChecked(json_settings.get_live_plot_IG_attribute("plot it") == "True")
        self.ui.IGPlotPressureLineStyle.setText(json_settings.get_live_plot_IG_attribute("pressure line style"))
        # CG1
        self.ui.CG1PlotItCheckBox.setChecked(json_settings.get_live_plot_CG1_attribute("plot it") == "True")
        self.ui.CG1PlotPressureLineStyle.setText(json_settings.get_live_plot_CG1_attribute("pressure line style"))
        # CG2
        self.ui.CG2PlotItCheckBox.setChecked(json_settings.get_live_plot_CG2_attribute("plot it") == "True")
        self.ui.CG2PlotPressureLineStyle.setText(json_settings.get_live_plot_CG2_attribute("pressure line style"))
        
        self.add_to_log_textbox(1, "Saved settings are loaded successfully")

        ########################
        # Logic, making UI work
        ########################
        ################
        # Help buttons
        ################
        # status bar help button
        def status_bar_help():
            msg = """in top bar you see:
             - Status of the device: if it's connected or not, with text indicating so and a colored dot (green connected, red not connected)
             - Feliment status: says if the feliment is on or off
             - Feliment power on/off button
             - Save settings button: when clicked, current paramaeters will be saved for future runs
             - Help button"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.actionHelpTopBarICO.triggered.connect(status_bar_help)

        # device port help
        def device_port_help():
            msg = """Enter the device port (e.g., COM1, /dev/ttyUSB0)
            Then click the connect button, you'll see a chnge in the status of the device at the top bar
            if you don't know the port of the device, opne 'Device Manager' and look under 'Ports (COM & LPT)' section"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.connectDeviceHelp.clicked.connect(device_port_help)

        # save file path help
        def save_file_path_help():
            msg = """Enter the path and file name of the data file you want to save the data to
            If left empty, a file will be created in the current directory with no name (will only have the name of the sensor)
            If 'Auto File Name' is checked it will use time to make the name and let you choose where to save it
            
            files format is csv
            sensor's name will be added to the end of the name of the file"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.SaveFilePathHelp.clicked.connect(save_file_path_help)

        # max runtime help
        def max_runtime_help():
            msg = """Enter the maximum time in seconds the program will run
            default is 0, program will run without stopping
            if a value is inserted, the program will stop after that time"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.maxRuntimeHelp.clicked.connect(max_runtime_help)
        
        # time latency help
        def time_latency_help():
            msg = """Enter the time in seconds to wait before starting the measurements
            default is 0, program will start immediately
            if a value is inserted, the program will wait that time before starting the measurements"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.timeLatencyHelp.clicked.connect(time_latency_help)

        # ig plot view help 
        def ig_plot_view_help():
            msg = """Check this box to plot the IG pressure
            You can change the line style of the pressure line: style is like matplotlib in python"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.IGplotHelp.clicked.connect(ig_plot_view_help)

        # cg1 plot view help
        def cg1_plot_view_help():
            msg = """Check this box to plot the CG1 pressure
            You can change the line style of the pressure line: style is like matplotlib in python"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.CG1plotHelp.clicked.connect(cg1_plot_view_help)

        # cg2 plot view help
        def cg2_plot_view_help():
            msg = """Check this box to plot the CG2 pressure
            You can change the line style of the pressure line: style is like matplotlib in python"""
            self.create_message_box("Help", msg, QMessageBox.Information)
        self.ui.CG2plotHelp.clicked.connect(cg2_plot_view_help)

        ################
        # Tool bar
        ################
        # feliment power button QAction
        def feliment_power_button():
            if hasattr(self, "CGDevice"):
                if self.CGDevice.get_feliment_status(): # feliment is on, turn it off
                    self.turn_feliment_off()
                else:
                    self.turn_feliment_on()
            else:
                # device not connected
                self.create_message_box("Error", "Device is not connected!", QMessageBox.Critical)
                self.add_to_log_textbox(1, "Can't turn on feliment - device is not connected!")
        self.ui.ToolBarPowerONOFFICO.triggered.connect(feliment_power_button)

        # save settings
        def save_settings():
            json_settings.save_settings()
            self.create_message_box("Success", "Settings saved successfully!", QMessageBox.Information)
            self.add_to_log_textbox(1, "Settings are saved successfully")
        self.ui.actionsaveSettingsICO.triggered.connect(save_settings)
        
        ################
        # Settings Tab
        ################
        ###########
        # Subtab 1
        ###########
        # device port
        def connect_device():
            # if device is already connected abort
            if hasattr(self, "CGDevice"):
                self.create_message_box("Warning", "Device is already connected!", QMessageBox.Warning)
                self.add_to_log_textbox(1, "Device is already connected - (connect button was clicked)")
                return

            port = self.ui.DevicePortLineEdit.text()
            try:
                self.CGDevice = CGcontacter.CGcontactor(port)
            except:
                self.create_message_box("Error", "Failed to connect to device!\nMake sure cable is connected and device is on", QMessageBox.Critical)
                self.add_to_log_textbox(1, "Failed to connect to device - make sure the cable is connected properly and the device is on, you can also validate device is connected in the 'Device Manager'")
                return

            # # call window.status_updater every 5 seconds
            # self.timer = QTimer()
            # # set the function as self.status_updater
            # self.timer.timeout.connect(self.status_updater)
            # self.timer.start(5000)
            
            self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(GREENDOT_ICON_PATH))
            self.ui.ToolBarStatusLabel.setText("Status: Connected")
            self.ui.connectDeviceButton.setIcon(QtGui.QIcon(CONNECTED_ICON_PATH))
            self.ui.connectDeviceLabel.setText("Connected")

            # check feliment status
            if self.CGDevice.get_feliment_status():
                self.ui.ToolBarFelimentLabel.setText("Feliment: ON")
                self.add_to_log_textbox(1, "Feliment is on")

            self.add_to_log_textbox(1, "Device is connected successfully")
        self.ui.connectDeviceButton.clicked.connect(connect_device)

        # device port line edit
        def device_port_line_edit_func():
            device_port = self.ui.DevicePortLineEdit.text()
            json_settings.set_settings_attribute("device port", device_port)
        self.ui.DevicePortLineEdit.textChanged.connect(device_port_line_edit_func)
        
        # save file
        def choose_file_path(x):
            default_name = 'default.csv'
            if self.ui.SaveFilePathCheckBox.isChecked():
                tmpstr = str(dt.datetime.now())
                default_name = f"{tmpstr.replace(':', '-')}.csv"
            
            default_directory = MEASUREMENTS_FOLDER_PATH + "/"
            file_filter = "CSV Files (*.csv)"

            options = QtWidgets.QFileDialog.Options()
            options |= QtWidgets.QFileDialog.DontUseNativeDialog  # Forces the native dialog

            filename, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                    "Save File",
                                                    default_directory + default_name,
                                                    file_filter,
                                                    options=options)
            # filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File", fileName, file_filter, options=options)[0]
            
            # filename = QtWidgets.QFileDialog.getSaveFileName(self)[0]
            if not filename.endswith(".csv"):
                filename += ".csv"
            self.ui.SaveFilePathLineEdit.setText(filename)
        self.ui.SaveFilePathLineEdit.mousePressEvent = choose_file_path

        # save file name on change
        def save_file_name_on_change(x):
            text = self.ui.SaveFilePathLineEdit.text()
            json_settings.set_settings_attribute("save data to", text)
        self.ui.SaveFilePathLineEdit.textChanged.connect(save_file_name_on_change)

        # auto file name checkox
        def auto_filename_checkbox(x):
            if self.ui.SaveFilePathCheckBox.isChecked():
                json_settings.set_settings_attribute("auto file name", "True")
                choose_file_path(x)
            else:
                json_settings.set_settings_attribute("auto file name", "False")
        self.ui.SaveFilePathCheckBox.stateChanged.connect(auto_filename_checkbox)

        ###########
        # Subtab 3
        ###########
        # max run time
        def max_run_time(x):
            text = str(self.ui.MaxRuntimeSpinBox.value())
            json_settings.set_settings_attribute("max runtime", text)
        self.ui.MaxRuntimeSpinBox.valueChanged.connect(max_run_time)

        # time latency
        def time_latency(x):
            text = str(self.ui.TimeLatencyDoubleSpinBox.value())
            json_settings.set_settings_attribute("time latency", text)
        self.ui.TimeLatencyDoubleSpinBox.valueChanged.connect(time_latency)

        # create log file check box
        def create_log_file(x):
            if self.ui.CreateLogFileCheckBox.isChecked():
                json_settings.set_settings_attribute("save log files", "True")
                log_obj.set_auto_save(True)
                log_obj.save_log()
            else:
                json_settings.set_settings_attribute("save log files", "False")
                log_obj.set_auto_save(False)
        self.ui.CreateLogFileCheckBox.stateChanged.connect(create_log_file)

        # start live plot push button
        def start_live_plot_button(x):
            # go to live-plot page
            self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.StartLivePlotPushButton.clicked.connect(start_live_plot_button)

        ################
        # Live-Plot Tab
        ################
        # IG #
        # plot it checkbox
        def IG_plot_it_checkbox_live_plot(x):
            if self.ui.IGPlotItCheckBox.isChecked():
                json_settings.set_live_plot_IG_attribute("plot it", "True")
            else:
                json_settings.set_live_plot_IG_attribute("plot it", "False")
        self.ui.IGPlotItCheckBox.stateChanged.connect(IG_plot_it_checkbox_live_plot)

        # pressure line style
        def IG_pressure_line_style_live_plot(x):
            text = self.ui.IGPlotPressureLineStyle.text()
            json_settings.set_live_plot_IG_attribute("pressure line style", text)
        self.ui.IGPlotPressureLineStyle.textChanged.connect(IG_pressure_line_style_live_plot)

        # CG1 #
        # plot it checkbox
        def CG1_plot_it_checkbox_live_plot(x):
            if self.ui.CG1PlotItCheckBox.isChecked():
                json_settings.set_live_plot_CG1_attribute("plot it", "True")
            else:
                json_settings.set_live_plot_CG1_attribute("plot it", "False")
        self.ui.CG1PlotItCheckBox.stateChanged.connect(CG1_plot_it_checkbox_live_plot)

        # pressure line style
        def CG1_pressure_line_style_live_plot(x):
            text = self.ui.CG1PlotPressureLineStyle.text()
            json_settings.set_live_plot_CG1_attribute("pressure line style", text)
        self.ui.CG1PlotPressureLineStyle.textChanged.connect(CG1_pressure_line_style_live_plot)

        # CG2 #
        # plot it checkbox
        def CG2_plot_it_checkbox_live_plot(x):
            if self.ui.CG2PlotItCheckBox.isChecked():
                json_settings.set_live_plot_CG2_attribute("plot it", "True")
            else:
                json_settings.set_live_plot_CG2_attribute("plot it", "False")
        self.ui.CG2PlotItCheckBox.stateChanged.connect(CG2_plot_it_checkbox_live_plot)

        # pressure line style
        def CG2_pressure_line_style_live_plot(x):
            text = self.ui.CG2PlotPressureLineStyle.text()
            json_settings.set_live_plot_CG2_attribute("pressure line style", text)
        self.ui.CG2PlotPressureLineStyle.textChanged.connect(CG2_pressure_line_style_live_plot)

        # pressure unit combo box
        def pressure_unit_combo_box_live_plot(x):
            text = self.ui.PlotPressureUnitCombo.currentText()
            json_settings.set_live_plot_attribute("pressure unit", text)
        self.ui.PlotPressureUnitCombo.currentIndexChanged.connect(pressure_unit_combo_box_live_plot)

        # time unit combo box
        def time_unit_combo_box_live_plot(x):
            text = self.ui.PlotTimeUnitCombo.currentText()
            json_settings.set_live_plot_attribute("time unit", text)
        self.ui.PlotTimeUnitCombo.currentIndexChanged.connect(time_unit_combo_box_live_plot)

        # gridded checkbox
        def gridded_checkbox(x):
            if self.ui.GriddedCheckBox.isChecked():
                json_settings.set_live_plot_attribute("gridded", "True")
            else:
                json_settings.set_live_plot_attribute("gridded", "False")
        self.ui.GriddedCheckBox.stateChanged.connect(gridded_checkbox)

        # x axis log scale checkbox
        def x_axis_log_scale_checkbox(x):
            if self.ui.XAxisLogScaleCheckbox.isChecked():
                json_settings.set_live_plot_attribute("x axis log scale", "True")
            else:
                json_settings.set_live_plot_attribute("x axis log scale", "False")
        self.ui.XAxisLogScaleCheckbox.stateChanged.connect(x_axis_log_scale_checkbox)

        # y axis log scale checkbox
        def y_axis_log_scale_checkbox(x):
            if self.ui.YAxisLogScaleCheckbox.isChecked():
                json_settings.set_live_plot_attribute("y axis log scale", "True")
            else:
                json_settings.set_live_plot_attribute("y axis log scale", "False")
        self.ui.YAxisLogScaleCheckbox.stateChanged.connect(y_axis_log_scale_checkbox)

        # start live plot button
        def start_live_plot(x):
            if not self.plot_controller:
                self.plot_controller = plotter.plotter()
            
            if not self.plot_controller.fig:
                self.plot_controller = plotter.plotter()
            
            if self.plot_controller.is_plot_on:
                self.create_message_box("Warning", "Plot already running!", QMessageBox.Warning)
                self.add_to_log_textbox(1, "Plot already running")
                return
            
            plot_name = "Pressure as a Function of Time"
            
            self.plot_controller.set_csv_file_path(self.ui.SaveFilePathLineEdit.text())

            pressure_unit = self.ui.PlotPressureUnitCombo.currentText()
            time_unit = self.ui.PlotTimeUnitCombo.currentText()
            self.plot_controller.pressure_unit = pressure_unit
            self.plot_controller.time_unit = time_unit
            xaxis_name = f"Time [{time_unit}]"
            yaxis_name = f"Pressure [{pressure_unit}]"
            
            xaxis_log_scale = self.ui.XAxisLogScaleCheckbox.isChecked()
            yaxis_log_scale = self.ui.YAxisLogScaleCheckbox.isChecked()
            gridded = self.ui.GriddedCheckBox.isChecked()
            
            self.plot_controller.set_plot_name(plot_name)
            self.plot_controller.set_xaxis_name(xaxis_name)
            self.plot_controller.set_yaxis_name(yaxis_name)
            self.plot_controller.set_xaxis_log(xaxis_log_scale)
            self.plot_controller.set_yaxis_log(yaxis_log_scale)
            self.plot_controller.set_gridded(gridded)
            
            # if IG plot is checked, add it
            if self.ui.IGPlotItCheckBox.isChecked():
                name = "IGP"
                style = self.ui.IGPlotPressureLineStyle.text()
                self.plot_controller.create_line(name, style)
                self.IGplotData = True
                self.plot_controller.create_csv_file("IGP")
            else:
                self.IGplotData = False
            
            # if CG1 plot is checked, add it
            if self.ui.CG1PlotItCheckBox.isChecked():
                name = "CG1P"
                style = self.ui.CG1PlotPressureLineStyle.text()
                self.plot_controller.create_line(name, style)
                self.CG1plotData = True
                self.plot_controller.create_csv_file("CG1P")
            else:
                self.CG1plotData = False
            
            # if CG2 plot is checked, add it
            if self.ui.CG2PlotItCheckBox.isChecked():
                name = "CG2P"
                style = self.ui.CG2PlotPressureLineStyle.text()
                self.plot_controller.create_line(name, style)
                self.CG2plotData = True
                self.plot_controller.create_csv_file("CG2P")
            else:
                self.CG2plotData = False
            
            self.start_time = time.time()
            self.plot_updater_can_run = True
            self.plot_controller.start_animation()
            
            def plot_data_updater():
                maxrunt = float(json_settings.get_settings_attribute("max runtime"))
                if maxrunt > 0 and time.time() - self.start_time > maxrunt:
                    close_live_plot(None)
                    self.plot_updater_can_run = False
                
                if not self.plot_updater_can_run:
                    return
                
                timefunc = json_units.get_time_function(self.plot_controller.time_unit)
                pressurefunc = json_units.get_pressure_function(self.plot_controller.pressure_unit)

                # if IG is plotted get it's pressure
                if self.IGplotData:
                    pressure = float(self.CGDevice.get_IG_pressure())
                    curtime = time.time() - self.start_time
                    
                    curtime = timefunc(curtime)
                    pressure = pressurefunc(pressure)

                    self.plot_controller.add_data("IGP", curtime, pressure)
                
                # ig CG1 is plotted get it's pressure
                if self.CG1plotData:
                    pressure = float(self.CGDevice.get_CG1_pressure())
                    curtime = time.time() - self.start_time

                    curtime = timefunc(curtime)
                    pressure = pressurefunc(pressure)
                    # print(f"\n\n\nhalo\n{curtime}\n{pressure}\n\n\n")
                    
                    self.plot_controller.add_data("CGP1", curtime, pressure)

            # create a timer runs every "time latency" and updates the graph
            self.plot_timer = QTimer()
            self.plot_timer.timeout.connect(plot_data_updater)
            self.plot_timer.start(int(float(json_settings.get_settings_attribute("time latency")) * 1000))
            self.add_to_log_textbox(1, "Live plot started")
        self.ui.StartPlotPlotView.clicked.connect(start_live_plot)

        # close live plot button
        def close_live_plot(x):
            if self.plot_controller:
                self.plot_controller.close_plot()
                self.plot_controller.is_plot_on = False
                # # stop animation
                # if self.plot_controller.ani:
                #     self.plot_controller.ani.event_source.stop()
                self.plot_controller = None
                # stop plot timer
                if self.plot_timer:
                    self.plot_timer.stop()
            else:
                self.create_message_box("Warning", "Plot does not exist!", QMessageBox.Warning)
                self.add_to_log_textbox(1, "Plot does not exist")
                return

            # stop self.plot_timer
            if self.plot_timer:
                self.plot_timer.stop()
            self.add_to_log_textbox(1, "Live plot closed")
        self.ui.StopPlotPlotView.clicked.connect(close_live_plot)

    # create message box
    def create_message_box(self, title:str, text:str, ico = QMessageBox.NoIcon):
        """ 
        icons in QMessageBox class:
            NoIcon, Information, Warning, Critical, Question
        """
        msgbox = QMessageBox()
        msgbox.setIcon(ico)
        msgbox.setText(text)
        msgbox.setWindowTitle(title)
        msgbox.setStandardButtons(QMessageBox.Ok)
        msgbox.exec_()
    
    # turn feliment on
    def turn_feliment_on(self):
        return
        if hasattr(self, "CGDevice"):
            # get feliment status
            if self.CGDevice.get_feliment_status():
                # feliment is already on
                self.add_to_log_textbox(1, "Feliment is already on")
                return
            if self.CGDevice.turn_feliment_on():
                self.create_message_box("Success", "Feliment turned on successfully!", QMessageBox.Information)
                self.ui.ToolBarFelimentLabel.setText("Feliment: ON")
                self.add_to_log_textbox(1, "Feliment turned on successfully")
            else:
                self.create_message_box("Error", "Failed to turn feliment on!", QMessageBox.Critical)
                self.add_to_log_textbox(1, "Failed to turn feliment on\nmake sure pressure is low enough!")
            # print("feliment onn")
            # self.add_to_log_textbox(1, "Feliment turned on successfully")
        else:
            self.create_message_box("Error", "Device is not connected!", QMessageBox.Critical)
            self.add_to_log_textbox(1, "Can't turn on feliment - device is not connected")

    # turn feliment off
    def turn_feliment_off(self):
        return
        if hasattr(self, "CGDevice"):
            # get feliment status
            if not self.CGDevice.get_feliment_status():
                # feliment is already off
                self.add_to_log_textbox(1, "Feliment is already off")
                return
            if self.CGDevice.turn_feliment_off():
                self.create_message_box("Success", "Feliment turned off successfully!", QMessageBox.Information)
                self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")
                self.add_to_log_textbox(1, "Feliment turned off successfully")
            else:
                self.create_message_box("Error", "Failed to turn feliment off!", QMessageBox.Critical)
                self.add_to_log_textbox(1, "Failed to turn feliment off")
        else:
            self.create_message_box("Error", "Device is not connected!", QMessageBox.Critical)
            self.add_to_log_textbox(1, "Can't turn off feliment - device is not connected")

    # set device status label and icon
    def set_device_status(self, status:bool):
        if status:
            self.ui.ToolBarStatusLabel.setText("Status: Connected")
            self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(GREENDOT_ICON_PATH))
        else:
            self.ui.ToolBarStatusLabel.setText("Status: Disconnected")
            self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(REDDOT_ICON_PATH))

    # status updater func
    def status_updater(self):
        # check if CGDevice is in self
        if not hasattr(self, "CGDevice"):
            # self.ui.ToolBarIGPLabel.setText("IGP: OFF")
            # self.ui.ToolBarCG1PLabel.setText("CG1P: OFF")
            # self.ui.ToolBarCG2PLabel.setText("CG2P: OFF")
            self.set_device_status(False)
            self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")
        else:
            # check if feliment is not safe to be on
            if self.CGDevice.is_feliment_safe_to_start() == False \
            and self.CGDevice.get_feliment_status() == True:
                # turn feliment off
                if not self.CGDevice.turn_feliment_off():
                    self.create_message_box("Error", "!!! Danger !!!\nfeliment should be turned off\nbut couldn't turn it off", QMessageBox.Critical)
                else:
                    self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")
                    self.create_message_box("Warning", "Feliment is not safe to be on!\nGot turned off automatically", QMessageBox.Warning)
                
            # feliment status
            if self.CGDevice.get_feliment_status():
                # feliment is on
                self.ui.ToolBarFelimentLabel.setText("Feliment: ON")
            else:
                # feliment is off
                self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")

            # IGP status
            if self.CGDevice.get_IG_status():
                # IGP is on
                # get pressure of IG
                pressure = self.CGDevice.get_IG_pressure()
                self.ui.ToolBarIGPLabel.setText(f"IGP: {pressure}")
                if self.IGplotData and self.plot_controller:
                    self.plot_controller.add_data_point("IGP", pressure)
            else:
                # IGP is off
                self.ui.ToolBarIGPLabel.setText("IGP: OFF")
            
            # CG1P status
            if self.CGDevice.get_CG1_status():
                # CG1P is on
                # get pressure of CG1
                pressure = self.CGDevice.get_CG1_pressure()
                self.ui.ToolBarCG1PLabel.setText(f"CG1P: {pressure}")
                if self.CG1plotData and self.plot_controller:
                    self.plot_controller.add_data_point("CGP1", pressure)
            else:
                # CG1P is off
                self.ui.ToolBarCG1PLabel.setText("CG1P: OFF")
            
            # CG2P status
            if self.CGDevice.get_CG2_status():
                # CG2P is on
                # get pressure of CG2
                pressure = self.CGDevice.get_CG2_pressure()
                self.ui.ToolBarCG2PLabel.setText(f"CG2P: {pressure}")
                if self.CG2plotData and self.plot_controller:
                    self.plot_controller.add_data_point("CGP2", pressure)
            else:
                # CG2P is off
                self.ui.ToolBarCG2PLabel.setText("CG2P: OFF")

    def add_to_log_textbox(self, to_add: bool, msg: str) -> None:
        if to_add:
            log_obj.add_message(msg)
        self.ui.LogTextBox1.setPlainText(log_obj.get_log_text())
        self.ui.LogTextBox2.setPlainText(log_obj.get_log_text())
        self.ui.LogTextBox3.setPlainText(log_obj.get_log_text())

        # set log textbox slider to be at the bottom
        self.ui.LogTextBox1.verticalScrollBar().setValue(self.ui.LogTextBox1.verticalScrollBar().maximum())
        self.ui.LogTextBox2.verticalScrollBar().setValue(self.ui.LogTextBox2.verticalScrollBar().maximum())
        self.ui.LogTextBox3.verticalScrollBar().setValue(self.ui.LogTextBox3.verticalScrollBar().maximum())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()

    # make a on close event
    def on_close(x):
        # close animation window if it's opened
        if window.plot_controller:
            window.plot_controller.close_plot()
        
        # # stop QTimer
        # window.timer.stop()

        # close the app
        app.quit()
    window.closeEvent = on_close
    
    window.add_to_log_textbox(1, "App started")

    window.show()
    # asyncio.run(sys.exit(app.exec_()))
    sys.exit(app.exec_())
