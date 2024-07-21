import time
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.animation as animation


class line:
    def __init__(self) -> None:
        self.x_data = []
        self.y_data = []
        self.name = ""
        self.style = ""

class plotter:
    def __init__(self) -> None:
        self.is_plot_on = False
        # create new figure
        self.fig = plt.figure()
        # remove the close button of the figure
        # self.fig.canvas.mpl_connect('close_event', lambda event: print("hi"))
        # create a plot area
        self.ax = self.fig.add_subplot(1, 1, 1)
        # list of lines
        self.lines = []
        self.lines_names = []
        # create a list for legends
        self.legends = []
        # is log scale?
        self.xaxis_is_log = False
        self.yaxis_is_log = False
        # data limits
        self.xlim = -1 # limitless
        self.ylim = -1 # limitless
        self.ani = None

        self.xaxis_name = ""
        self.yaxis_name = ""
        self.plot_name = ""
        self.fig_name = ""
        self.gridded = False

    def animate(self, i: int) -> None:
        # clear the plot area
        self.ax.clear()
        # set title
        self.ax.set_title(self.plot_name)
        # set labels
        self.ax.set_xlabel(self.xaxis_name)
        self.ax.set_ylabel(self.yaxis_name)
        # set log scale
        if self.xaxis_is_log:
            self.ax.set_xscale('log')
        if self.yaxis_is_log:
            self.ax.set_yscale('log')
        # set grid
        self.ax.grid(self.gridded)
        # set data limits
        if self.xlim != -1:
            self.ax.set_xlim(0, self.xlim)
        if self.ylim != -1:
            self.ax.set_ylim(0, self.ylim)
        # plot data
        for line in self.lines:
            self.ax.plot(line.x_data, line.y_data, line.style, label=line.name)
        # legend with legend names
        self.ax.legend(self.legends)
        # auto scale
        self.ax.relim()
        self.ax.autoscale_view()
        # draw the plot
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def set_fig_name(self, name: str) -> None:
        self.fig_name = name
        self.fig.canvas.set_window_title(name)
    
    def set_plot_name(self, name: str) -> None:
        self.plot_name = name
        self.ax.set_title(name)
    
    def set_xaxis_name(self, name: str) -> None:
        self.xaxis_name = name
        self.ax.set_xlabel(name)
    
    def set_yaxis_name(self, name: str) -> None:
        self.yaxis_name = name
        self.ax.set_ylabel(name)
    
    def set_xaxis_log(self, is_log: bool) -> None:
        self.xaxis_is_log = is_log
        if is_log:
            self.ax.set_xscale('log')

    def set_yaxis_log(self, is_log: bool) -> None:
        self.yaxis_is_log = is_log
        if is_log:
            self.ax.set_yscale('log')
    
    def set_gridded(self, is_gridded: bool) -> None:
        self.gridded = is_gridded
        self.ax.grid(is_gridded)
    
    def create_line(self, name: str, style = "") -> None:
        new_line = line()
        new_line.name = name
        new_line.style = style
        self.lines.append(new_line)
        self.lines_names.append(name)
    
    def set_line_style(self, name: str, style: str) -> None:
        if name not in self.lines_names:
            return
        id = self.lines_names.index(name)
        self.lines[id].style = style
    
    def add_data(self, name: str, x: float, y: float) -> None:
        if name not in self.lines_names:
            return
        id = self.lines_names.index(name)
        self.lines[id].x_data.append(x)
        self.lines[id].y_data.append(y)
    
    def set_data_xlim(self, xlim: float) -> None:
        self.xlim = xlim

    def set_data_ylim(self, ylim: float) -> None:
        self.ylim = ylim
    
    def start_animation(self) -> None:
        if not self.ani:
            self.ani = animation.FuncAnimation(self.fig, self.animate, interval=1000, cache_frame_data=False)

        # make a on close event for figure
        def on_close(event):
            self.close_plot()
            # remove figure from the list of figures
            plt.close(self.fig)
            self.fig = None
        self.fig.canvas.mpl_connect('close_event', on_close)

        self.is_plot_on = True
        plt.show()
    
    def stop_animation(self) -> None:
        self.ani.event_source.stop()
    
    def clear_plot(self) -> None:
        self.ax.clear()
    
    def refresh_plot(self) -> None:
        self.stop_animation()
        self.clear_data()
        self.clear_plot()
        self.start_animation()
    
    def clear_data(self) -> None:
        # remove all data and lines
        for line in self.lines:
            line.x_data.clear()
            line.y_data.clear()
    
    def close_plot(self) -> None:
        self.is_plot_on = False
        plt.close(self.fig)
        # clear all data
        self.clear_data()
        self.lines.clear()
