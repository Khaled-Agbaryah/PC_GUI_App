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

log_obj = logger.logger(f"{LOG_FOLDER_PATH}/{dt.datetime.now()}")
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
        self.ui.BufferingHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.IGSectionHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG1SectionHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG2SectionHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.maxRuntimeHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.timeLatencyHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.IGplotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG1plotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))
        self.ui.CG2plotHelp.setIcon(QtGui.QIcon(HELP_ICON_PATH))

        # insert values into ComboBoxes
        pressure_units = json_units.get_pressure_units()
        time_units = json_units.get_time_units()
        self.ui.IGPressureUnitCombo.insertItems(0, pressure_units[:])
        self.ui.IGTimeUnitCombo.insertItems(0, time_units[:])
        self.ui.CG1PressureUnitCombo.insertItems(0, pressure_units[:])
        self.ui.CG1TimeUnitCombo.insertItems(0, time_units[:])
        self.ui.CG2PressureUnitCombo.insertItems(0, pressure_units[:])
        self.ui.CG2TimeUnitCombo.insertItems(0, time_units[:])

        # insert Help Page content
        with open(HELP_PAGE_TEXT_FILE_PATH, "r") as fp:
            self.ui.helpPageLabel.setText(fp.read())
 
        # settings page tabs names
        self.ui.tabWidget.setTabText(0, SETTINGS_TAB_SUBTAB_1_NAME)
        self.ui.tabWidget.setTabText(1, SETTINGS_TAB_SUBTAB_2_NAME)
        self.ui.tabWidget.setTabText(2, SETTINGS_TAB_SUBTAB_3_NAME)

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
        self.ui.BufferingCheckBox.setChecked(json_settings.get_settings_attribute("data buffering") == "True")
        tmp = str(json_settings.get_settings_attribute("buffer max size"))
        tmp = int(tmp) if is_int(tmp) else 0
        self.ui.BufferingSpinBox.setValue(tmp)
        # tab2 #
        # IG
        self.ui.IGSaveToFileCheckBox.setChecked(json_settings.get_settings_IG_attribute("save to file") == "True")
        self.ui.IGPressureUnitCombo.setCurrentText(json_settings.get_settings_IG_attribute("pressure unit"))
        self.ui.IGTimeUnitCombo.setCurrentText(json_settings.get_settings_IG_attribute("time unit"))
        self.ui.IGCustomFunctionLineEdit.setText(json_settings.get_settings_IG_attribute("custom function"))
        # CG1
        self.ui.CG1SaveToFileCheckBox.setChecked(json_settings.get_settings_CG1_attribute("save to file") == "True")
        self.ui.CG1PressureUnitCombo.setCurrentText(json_settings.get_settings_CG1_attribute("pressure unit"))
        self.ui.CG1TimeUnitCombo.setCurrentText(json_settings.get_settings_CG1_attribute("time unit"))
        self.ui.CG1CustomFunctionLineEdit.setText(json_settings.get_settings_CG1_attribute("custom function"))
        # CG2
        self.ui.CG2SaveToFileCheckBox.setChecked(json_settings.get_settings_CG2_attribute("save to file") == "True")
        self.ui.CG2PressureUnitCombo.setCurrentText(json_settings.get_settings_CG2_attribute("pressure unit"))
        self.ui.CG2TimeUnitCombo.setCurrentText(json_settings.get_settings_CG2_attribute("time unit"))
        self.ui.CG2CustomFunctionLineEdit.setText(json_settings.get_settings_CG2_attribute("custom function"))
        # tab3 #
        tmp = str(json_settings.get_settings_attribute("max runtime"))
        tmp = int(tmp) if is_int(tmp) else 0
        self.ui.MaxRuntimeSpinBox.setValue(tmp)
        tmp = str(json_settings.get_settings_attribute("time latency"))
        tmp = float(tmp) if is_float(tmp) else 0
        self.ui.TimeLatencyDoubleSpinBox.setValue(tmp)
        self.ui.CreateLogFileCheckBox.setChecked(json_settings.get_settings_attribute("save log files") == "True")
        ## live plot ##
        # IG
        self.ui.IGPlotItCheckBox.setChecked(json_settings.get_live_plot_IG_attribute("plot it") == "True")
        self.ui.IGPlotCustomFunctionLineEdit.setText(json_settings.get_live_plot_IG_attribute("custom function"))
        self.ui.IGPlotPressureLineStyle.setText(json_settings.get_live_plot_IG_attribute("pressure line style"))
        self.ui.IGPlotCustomFunctionLineStyle.setText(json_settings.get_live_plot_IG_attribute("custom function line style"))
        # CG1
        self.ui.CG1PlotItCheckBox.setChecked(json_settings.get_live_plot_CG1_attribute("plot it") == "True")
        self.ui.CG1PlotCustomFunctionLineEdit.setText(json_settings.get_live_plot_CG1_attribute("custom function"))
        self.ui.CG1PlotPressureLineStyle.setText(json_settings.get_live_plot_CG1_attribute("pressure line style"))
        self.ui.CG1PlotCustomFunctionLineStyle.setText(json_settings.get_live_plot_CG1_attribute("custom function line style"))
        # CG2
        self.ui.CG2PlotItCheckBox.setChecked(json_settings.get_live_plot_CG2_attribute("plot it") == "True")
        self.ui.CG2PlotCustomFunctionLineEdit.setText(json_settings.get_live_plot_CG2_attribute("custom function"))
        self.ui.CG2PlotPressureLineStyle.setText(json_settings.get_live_plot_CG2_attribute("pressure line style"))
        self.ui.CG2PlotCustomFunctionLineStyle.setText(json_settings.get_live_plot_CG2_attribute("custom function line style"))
        
        ########################
        # Logic, making UI work
        ########################
        ################
        # general
        ################
        
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
        self.ui.ToolBarPowerONOFFICO.triggered.connect(feliment_power_button)

        # save settings
        def save_settings():
            json_settings.save_settings()
            self.create_message_box("Success", "Settings saved successfully!", QMessageBox.Information)
            
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
                return

            port = self.ui.DevicePortLineEdit.text()
            try:
                self.CGDevice = CGcontacter.CGcontactor(port)
            except:
                self.create_message_box("Error", "Failed to connect to device!\nMake sure cable is connected and device is on", QMessageBox.Critical)
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
            
            default_directory = './measurements/'
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

            log_obj.set_log_file_path(filename)
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

        # data buffering checkbox
        def data_buffering_checkbox(x):
            if self.ui.BufferingCheckBox.isChecked():
                json_settings.set_settings_attribute("data buffering", "True")
            else:
                json_settings.set_settings_attribute("data buffering", "False")
        self.ui.BufferingCheckBox.stateChanged.connect(data_buffering_checkbox)

        # buffer max size
        def buffer_max_size(x):
            text = str(self.ui.BufferingSpinBox.value())
            json_settings.set_settings_attribute("buffer max size", text)
        self.ui.BufferingSpinBox.valueChanged.connect(buffer_max_size)

        ###########
        # Subtab 2
        ###########
        # IG #
        # save to file checkbox
        def IG_save_to_file_checkbox(x):
            if self.ui.IGSaveToFileCheckBox.isChecked():
                json_settings.set_settings_IG_attribute("save to file", "True")
            else:
                json_settings.set_settings_IG_attribute("save to file", "False")
        self.ui.IGSaveToFileCheckBox.stateChanged.connect(IG_save_to_file_checkbox)

        # pressure unit combo box
        def IG_pressure_unit_combo_box(x):
            text = self.ui.IGPressureUnitCombo.currentText()
            json_settings.set_settings_IG_attribute("pressure unit", text)
        self.ui.IGPressureUnitCombo.currentIndexChanged.connect(IG_pressure_unit_combo_box)

        # time unit combo box
        def IG_time_unit_combo_box(x):
            text = self.ui.IGTimeUnitCombo.currentText()
            json_settings.set_settings_IG_attribute("time unit", text)
        self.ui.IGTimeUnitCombo.currentIndexChanged.connect(IG_time_unit_combo_box)

        # custom function
        def IG_custom_function(x):
            text = self.ui.IGCustomFunctionLineEdit.text()
            json_settings.set_settings_IG_attribute("custom function", text)
        self.ui.IGCustomFunctionLineEdit.textChanged.connect(IG_custom_function)

        # CG1 #
        # save to file checkbox
        def CG1_save_to_file_checkbox(x):
            if self.ui.CG1SaveToFileCheckBox.isChecked():
                json_settings.set_settings_CG1_attribute("save to file", "True")
            else:
                json_settings.set_settings_CG1_attribute("save to file", "False")
        self.ui.CG1SaveToFileCheckBox.stateChanged.connect(CG1_save_to_file_checkbox)

        # pressure unit combo box
        def CG1_pressure_unit_combo_box(x):
            text = self.ui.CG1PressureUnitCombo.currentText()
            json_settings.set_settings_CG1_attribute("pressure unit", text)
        self.ui.CG1PressureUnitCombo.currentIndexChanged.connect(CG1_pressure_unit_combo_box)

        # time unit combo box
        def CG1_time_unit_combo_box(x):
            text = self.ui.CG1TimeUnitCombo.currentText()
            json_settings.set_settings_CG1_attribute("time unit", text)
        self.ui.CG1TimeUnitCombo.currentIndexChanged.connect(CG1_time_unit_combo_box)

        # custom function
        def CG1_custom_function(x):
            text = self.ui.CG1CustomFunctionLineEdit.text()
            json_settings.set_settings_CG1_attribute("custom function", text)
        self.ui.CG1CustomFunctionLineEdit.textChanged.connect(CG1_custom_function)

        # CG2 #
        # save to file checkbox
        def CG2_save_to_file_checkbox(x):
            if self.ui.CG2SaveToFileCheckBox.isChecked():
                json_settings.set_settings_CG2_attribute("save to file", "True")
            else:
                json_settings.set_settings_CG2_attribute("save to file", "False")
        self.ui.CG2SaveToFileCheckBox.stateChanged.connect(CG2_save_to_file_checkbox)

        # pressure unit combo box
        def CG2_pressure_unit_combo_box(x):
            text = self.ui.CG2PressureUnitCombo.currentText()
            json_settings.set_settings_CG2_attribute("pressure unit", text)
        self.ui.CG2PressureUnitCombo.currentIndexChanged.connect(CG2_pressure_unit_combo_box)

        # time unit combo box
        def CG2_time_unit_combo_box(x):
            text = self.ui.CG2TimeUnitCombo.currentText()
            json_settings.set_settings_CG2_attribute("time unit", text)
        self.ui.CG2TimeUnitCombo.currentIndexChanged.connect(CG2_time_unit_combo_box)

        # custom function
        def CG2_custom_function(x):
            text = self.ui.CG2CustomFunctionLineEdit.text()
            json_settings.set_settings_CG2_attribute("custom function", text)
        self.ui.CG2CustomFunctionLineEdit.textChanged.connect(CG2_custom_function)

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
            else:
                json_settings.set_settings_attribute("save log files", "False")
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

        # custom function
        def IG_custom_function_live_plot(x):
            text = self.ui.IGPlotCustomFunctionLineEdit.text()
            json_settings.set_live_plot_IG_attribute("custom function", text)
        self.ui.IGPlotCustomFunctionLineEdit.textChanged.connect(IG_custom_function_live_plot)

        # pressure line style
        def IG_pressure_line_style_live_plot(x):
            text = self.ui.IGPlotPressureLineStyle.text()
            json_settings.set_live_plot_IG_attribute("pressure line style", text)
        self.ui.IGPlotPressureLineStyle.textChanged.connect(IG_pressure_line_style_live_plot)

        # custome function line style
        def IG_custom_function_line_style_live_plot(x):
            text = self.ui.IGPlotCustomFunctionLineStyle.text()
            json_settings.set_live_plot_IG_attribute("custom function line style", text)
        self.ui.IGPlotCustomFunctionLineStyle.textChanged.connect(IG_custom_function_line_style_live_plot)

        # CG1 #
        # plot it checkbox
        def CG1_plot_it_checkbox_live_plot(x):
            if self.ui.CG1PlotItCheckBox.isChecked():
                json_settings.set_live_plot_CG1_attribute("plot it", "True")
            else:
                json_settings.set_live_plot_CG1_attribute("plot it", "False")
        self.ui.CG1PlotItCheckBox.stateChanged.connect(CG1_plot_it_checkbox_live_plot)

        # custom function
        def CG1_custom_function_live_plot(x):
            text = self.ui.CG1PlotCustomFunctionLineEdit.text()
            json_settings.set_live_plot_CG1_attribute("custom function", text)
        self.ui.CG1PlotCustomFunctionLineEdit.textChanged.connect(CG1_custom_function_live_plot)

        # pressure line style
        def CG1_pressure_line_style_live_plot(x):
            text = self.ui.CG1PlotPressureLineStyle.text()
            json_settings.set_live_plot_CG1_attribute("pressure line style", text)
        self.ui.CG1PlotPressureLineStyle.textChanged.connect(CG1_pressure_line_style_live_plot)

        # custome function line style
        def CG1_custom_function_line_style_live_plot(x):
            text = self.ui.CG1PlotCustomFunctionLineStyle.text()
            json_settings.set_live_plot_CG1_attribute("custom function line style", text)
        self.ui.CG1PlotCustomFunctionLineStyle.textChanged.connect(CG1_custom_function_line_style_live_plot)
        
        # CG2 #
        # plot it checkbox
        def CG2_plot_it_checkbox_live_plot(x):
            if self.ui.CG2PlotItCheckBox.isChecked():
                json_settings.set_live_plot_CG2_attribute("plot it", "True")
            else:
                json_settings.set_live_plot_CG2_attribute("plot it", "False")
        self.ui.CG2PlotItCheckBox.stateChanged.connect(CG2_plot_it_checkbox_live_plot)

        # custom function
        def CG2_custom_function_live_plot(x):
            text = self.ui.CG2PlotCustomFunctionLineEdit.text()
            json_settings.set_live_plot_CG2_attribute("custom function", text)
        self.ui.CG2PlotCustomFunctionLineEdit.textChanged.connect(CG2_custom_function_live_plot)

        # pressure line style
        def CG2_pressure_line_style_live_plot(x):
            text = self.ui.CG2PlotPressureLineStyle.text()
            json_settings.set_live_plot_CG2_attribute("pressure line style", text)
        self.ui.CG2PlotPressureLineStyle.textChanged.connect(CG2_pressure_line_style_live_plot)

        # custome function line style
        def CG2_custom_function_line_style_live_plot(x):
            text = self.ui.CG2PlotCustomFunctionLineStyle.text()
            json_settings.set_live_plot_CG2_attribute("custom function line style", text)
        self.ui.CG2PlotCustomFunctionLineStyle.textChanged.connect(CG2_custom_function_line_style_live_plot)

        # pressure unit combo box
        def CG2_pressure_unit_combo_box_live_plot(x):
            text = self.ui.PlotPressureUnitCombo.currentText()
            json_settings.set_live_plot_attribute("pressure unit", text)
        self.ui.PlotPressureUnitCombo.currentIndexChanged.connect(CG2_pressure_unit_combo_box_live_plot)

        # time unit combo box
        def CG2_time_unit_combo_box_live_plot(x):
            text = self.ui.PlotTimeUnitCombo.currentText()
            json_settings.set_live_plot_attribute("time unit", text)
        self.ui.PlotTimeUnitCombo.currentIndexChanged.connect(CG2_time_unit_combo_box_live_plot)

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
                return
            
            plot_name = "Pressure as a Function of Time"
            
            pressure_unit = self.ui.IGPressureUnitCombo.currentText()
            time_unit = self.ui.IGTimeUnitCombo.currentText()
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
                style = self.ui.IGPlotItCheckBox.text()
                self.plot_controller.create_line(name, style)
                self.IGplotData = True
            else:
                self.IGplotData = False
            
            # if CG1 plot is checked, add it
            if self.ui.CG1PlotItCheckBox.isChecked():
                name = "CGP1"
                style = self.ui.CG1PlotItCheckBox.text()
                self.plot_controller.create_line(name, style)
                self.CG1plotData = True
            else:
                self.CG1plotData = False
            
            # # if CG2 plot is checked, add it
            # if self.ui.CG2PlotItCheckBox.isChecked():
            #     name = "CGP2"
            #     style = self.ui.CG2PlotItCheckBox.text()
            #     self.plot_controller.create_line(name, style)
            #     self.CG2plotData = True
            # else:
            #     self.CG2plotData = False
            
            self.start_time = time.time()
            self.plot_controller.start_animation()
            
            # create a timer runs every "time latency" and updates the graph
            self.plot_timer = QTimer()
            self.plot_timer.timeout.connect(self.plot_data_updater)
            self.plot_timer.start(json_settings.get_settings_attribute("time latency") * 1000)

        self.ui.StartPlotPlotView.clicked.connect(start_live_plot)

        # close live plot button
        def close_live_plot(x):
            if self.plot_controller:
                self.plot_controller.close_plot()
                self.plot_controller = None
            else:
                self.create_message_box("Warning", "Plot does not exist!", QMessageBox.Warning)

            # stop self.plot_timer
            if self.plot_timer:
                self.plot_timer.stop()
        self.ui.StopPlotPlotView.clicked.connect(close_live_plot)

    def plot_data_updater(self):
        timefunc = json_units.get_time_function(self.plot_controller.time_unit)
        pressurefunc = json_units.get_pressure_function(self.plot_controller.pressure_unit)

        # if IG is plotted get it's pressure
        if self.IGplotData:
            pressure = self.CGDevice.get_IG_pressure()
            curtime = time.time() - self.start_time

            self.plot_controller.add_data("IGP", timefunc(curtime), pressurefunc(pressure))
        
        # ig CG1 is plotted get it's pressure
        if self.CG1plotData:
            pressure = self.CGDevice.get_CG1_pressure()
            curtime = time.time() - self.start_time

            self.plot_controller.add_data("CGP1", timefunc(curtime), pressurefunc(pressure))

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
        if hasattr(self, "CGDevice"):
            # get feliment status
            if self.CGDevice.get_feliment_status():
                # feliment is already on
                return
            # if self.CGDevice.turn_feliment_on():
            #     self.create_message_box("Success", "Feliment turned on successfully!", QMessageBox.Information)
            #     self.ui.ToolBarFelimentLabel.setText("Feliment: ON")
            # else:
            #     self.create_message_box("Error", "Failed to turn feliment on!", QMessageBox.Critical)
            print("feliment onn")
        else:
            self.create_message_box("Error", "Device is not connected!", QMessageBox.Critical)
    
    # turn feliment off
    def turn_feliment_off(self):
        if hasattr(self, "CGDevice"):
            # get feliment status
            if not self.CGDevice.get_feliment_status():
                # feliment is already off
                return
            if self.CGDevice.turn_feliment_off():
                self.create_message_box("Success", "Feliment turned off successfully!", QMessageBox.Information)
                self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")
            else:
                self.create_message_box("Error", "Failed to turn feliment off!", QMessageBox.Critical)
        else:
            self.create_message_box("Error", "Device is not connected!", QMessageBox.Critical)
    
    # set device status label and icon
    def set_device_status(self, status:bool):
        if status:
            self.ui.ToolBarStatusLabel.setText("Status: Connected")
            self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(GREENDOT_ICON_PATH))
        else:
            self.ui.ToolBarStatusLabel.setText("Status: Disconnected")
            self.ui.ToolBarStatusdot.setIcon(QtGui.QIcon(REDDOT_ICON_PATH))

    # status updater func
    async def status_updater(self):
        # check if CGDevice is in self
        if not hasattr(self, "CGDevice"):
            self.ui.ToolBarIGPLabel.setText("IGP: OFF")
            self.ui.ToolBarCG1PLabel.setText("CG1P: OFF")
            self.ui.ToolBarCG2PLabel.setText("CG2P: OFF")
            self.set_device_status(False)
            self.ui.ToolBarFelimentLabel.setText("Feliment: OFF")
        else:
            # check if feliment is not safe to be on
            if await self.CGDevice.is_feliment_safe_to_start() == False \
            and await self.CGDevice.get_feliment_status() == True:
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
        
        self.__render_log_textbox()

    def __render_log_textbox(self) -> None:
        self.ui.LogTextBox1.setPlainText(log_obj.get_log_text())
        self.ui.LogTextBox2.setPlainText(log_obj.get_log_text())


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
    
    window.show()
    # asyncio.run(sys.exit(app.exec_()))
    sys.exit(app.exec_())
