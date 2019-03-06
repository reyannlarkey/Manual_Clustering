import pandas as pd
import numpy as np
import cartopy.crs as ccrs
from itertools import cycle
from matplotlib.widgets import LassoSelector, Button, PolygonSelector, RadioButtons
import matplotlib.pyplot as plt
from matplotlib.path import Path
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import os
from tkinter import filedialog
import tkinter as TK

class SelectFromCollection(object):
    def __init__(self, fig, ax, collection, df, savefolder, savefile,  filelist = []):
        self.fig = fig
        self.ax = ax
        self.df = df
        self.savefolder = savefolder
        global saveME
        saveME = savefile
        self.savefile = savefile

        self.filelist = filelist
        self.current_file = 0

        self.last_file = len(filelist)-1

        self.df['cluster'] = -1
        self.cluster_count = 0
        self.canvas = ax.figure.canvas
        self.collection = collection

        self.xys = collection.get_offsets()
        self.Npts = len(self.xys)

        # Ensure that we have separate colors for each object
        self.fc = collection.get_facecolors()
        self.ec = collection.get_edgecolors()

        if len(self.fc) == 0:
            raise ValueError('Collection must have a facecolor')
        elif len(self.fc) == 1:
            self.fc = np.tile(self.fc, (self.Npts, 1))
            self.ec = np.tile(self.ec, (self.Npts, 1))
        self.lasso = PolygonSelector(ax, onselect=self.onselect)
        self.ind = []
        self.color_list = cycle(np.arange(0, 1, 0.1))
        self.color_list2 = cycle(np.arange(0, 1, 0.3))

    def onselect(self, verts):
        path = Path(verts)
        self.ind = np.nonzero(path.contains_points(self.xys))[0]
        self.collection.set_facecolors(self.fc)
        self.collection.set_facecolors(self.ec)
        self.canvas.draw()

    def entered(self):
        self.df.iloc[self.ind, 3] = self.cluster_count
        self.cluster_count += 1
        self.fc[self.ind, 1] = next(self.color_list)
        self.fc[self.ind, 0] = next(self.color_list2)
        self.ec[self.ind, 1] = next(self.color_list)
        self.ec[self.ind, 0] = next(self.color_list2)

        self.collection.set_facecolors(self.fc)
        self.collection.set_edgecolors(self.ec)
        self.canvas.draw_idle()

    def save(self, event):
        saved_file = os.path.join(self.savefolder, 'manually_clustered',os.path.basename(saveME) )
        # os.makedirs(os.path.dirname(filename), exist_ok=True)
        # with open(filename, "w") as f:
        #     f.write("FOOBAR")
        os.makedirs(os.path.dirname(saved_file), exist_ok=True)
        self.df['probs'] = 1
        self.df['out'] = 0
        self.df.to_csv(path_or_buf=saved_file, index=False, header = None, sep = '\t')
        print("File Saved As:", saved_file)

    def close(self, event):
        plt.close(fig=self.fig)




class cluster_manually():
    def __init__(self, file_or_folder = "/mnt/driveA/ENTLN_Processing/Merged"):
        self.file_or_folder = file_or_folder
        self.current_index = 0
        root = TK.Tk()
        root.title("What would you like to cluster?")
        root.geometry("400x20")
        root.configure( background="darkgrey")
        frame = TK.Frame(root)
        frame.pack()

        button = TK.Button(frame,
                           text="Entire Folder of events",
                           fg="white",
                           bg = '#37455b',
                           command=lambda: [f() for f in [self.folder_select, root.quit]])
        button.pack(side=TK.LEFT)
        button2 = TK.Button(frame,
                           text="Individual events",
                           bg = '#37455b',
                           fg = 'white',
                           command=lambda: [f() for f in [self.file_select, root.quit]])
        button2.pack(side=TK.LEFT)
        root.mainloop()


        self.update_data(file = self.files_list[0])
        subplot_kw = dict(autoscale_on=True, projection=ccrs.PlateCarree())
        self.fig, self.ax = plt.subplots(subplot_kw=subplot_kw, figsize=(10, 10))
        plt.subplots_adjust(bottom=0.2)
        pts = self.ax.scatter(self.location_df['lon'], self.location_df['lat'], s=15, color='grey')
        self.selector = SelectFromCollection(self.fig, self.ax, pts, df=self.df,savefolder = self.save_path, savefile = self.files_list[self.current_index],
                                            filelist=self.files_list)
        self.ax.set_extent([min(self.df['Longitude'])-1, max(self.df['Longitude'])+1, min(self.df['Latitude'])-1, max(self.df['Latitude'])+1])

        axsave = plt.axes([0.1, 0.05, 0.1, 0.075])
        bsave = Button(axsave, 'Save', color = 'red')
        bsave.on_clicked(self.selector.save)

        axclose = plt.axes([0.81, 0.05, 0.1, 0.075])
        bclose = Button(axclose, 'close')
        bclose.on_clicked(self.selector.close)

        axprev = plt.axes([0.37, 0.05, 0.1, 0.075])
        bprev = Button(axprev, 'Previous', color = 'darkgrey')
        bprev.on_clicked(self.prev_file)

        axnext = plt.axes([0.53, 0.05, 0.1, 0.075])
        bnext = Button(axnext, 'Next', color = 'darkgrey')
        bnext.on_clicked(self.next_file)

        self.fig.canvas.mpl_connect("key_press_event", self.accept)
        self.ax.set_title(self.files_list[0])
        self.fig.suptitle("Press: 'F1' to accept \n"
                          "Press: 'esc' to move Polygon", color = 'red')


        self.ax.coastlines()
        self.ax.text(-0.125, 0.55, 'Latitude', va='bottom', ha='center',
                rotation='vertical', rotation_mode='anchor',
                transform=self.ax.transAxes)
        self.ax.text(0.5, -0.1, 'Longitude', va='bottom', ha='center',
                rotation='horizontal', rotation_mode='anchor',
                transform=self.ax.transAxes)
        gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=2, color='gray', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = True
        gl.ylabels_right = False

        plt.show()




    def folder_select(self):
        self.path = filedialog.askdirectory(initialdir=self.file_or_folder)
        files = os.listdir(self.path)
        files_list = []
        for i in files:
            files_list.append(os.path.join(self.path, i))
        self.files_list = files_list
        self.save_path = self.path

    def file_select(self):
        self.path = filedialog.askopenfilenames(initialdir = self.file_or_folder)
        self.files_list = (list(self.path))
        self.save_path = os.path.dirname(self.files_list[0])

    def start_clustering(self):
        files = self.files_list
        self.current_index = 0
        self.update_data(file= files[self.current_index])
        self.plot_clusters()

    def next_file(self, event):
        if self.current_index == len(self.files_list)-1:
            pass
        else:
            self.current_index += 1
            file = self.files_list[self.current_index]
            self.update_data(file = file)
            self.ax.clear()
            self.plot_clusters()
            plt.draw()

    def prev_file(self, event):
        if self.current_index ==0:
            pass
        else:
            self.current_index -= 1
            file = self.files_list[self.current_index]
            self.update_data(file = file)
            self.ax.clear()
            self.plot_clusters()
            plt.draw()
    def update_data(self, file="empty.txt"):
        # --------------------------------------------------------DATA----------------------------------------------------
        df = pd.read_csv(file, usecols=['Latitude', 'Longitude', 'TotalSeconds'])


        self.location_df = pd.DataFrame({
            'lat': df['Latitude'].values,
            'lon': df['Longitude'].values
        })

        self.time_df = pd.DataFrame({
            't': df['TotalSeconds'].values
        })

        len_of_data = len(self.time_df['t'].values)
        savefile = self.files_list[self.current_index]
        self.df = df[['Latitude', 'Longitude', 'TotalSeconds']]
        # ----------------------------------------------------------------------------------------------------------------

    def plot_clusters(self):
        pts = self.ax.scatter(self.location_df['lon'], self.location_df['lat'], s=15, color= 'grey')
        self.selector = SelectFromCollection(self.fig, self.ax, pts, df = self.df, savefolder = self.save_path,savefile = self.files_list[self.current_index], filelist = self.files_list)
        self.ax.set_extent([min(self.df['Longitude'])-1, max(self.df['Longitude'])+1, min(self.df['Latitude'])-1, max(self.df['Latitude'])+1])
        self.ax.coastlines()
        self.ax.text(-0.125, 0.55, 'Latitude', va='bottom', ha='center',
                     rotation='vertical', rotation_mode='anchor',
                     transform=self.ax.transAxes)
        self.ax.text(0.5, -0.1, 'Longitude', va='bottom', ha='center',
                     rotation='horizontal', rotation_mode='anchor',
                     transform=self.ax.transAxes)
        self.ax.set_title(self.files_list[self.current_index])
        self.fig.suptitle("Press: 'F1' to accept \n"
                          "Press: 'esc' to move Polygon", color = 'red')
        gl = self.ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                               linewidth=2, color='gray', alpha=0.5, linestyle='--')
        gl.xlabels_top = False
        gl.ylabels_left = True
        gl.ylabels_right = False
        plt.draw()

    def accept(self, event):
        if event.key == "f1":
            self.selector.entered()
            self.fig.canvas.draw()

if __name__ == "__main__":
    cwd = os.getcwd()
    cluster_manually(file_or_folder = cwd)
