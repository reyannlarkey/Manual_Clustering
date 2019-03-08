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


class cluster_manually():
    def __init__(self, file_or_folder = "/mnt/driveA/ENTLN_Processing/Merged"):
        self.file_or_folder = file_or_folder
        self.current_index = 0
        self.choose_data()



    def choose_data(self):
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


if __name__ == "__main__":
    cwd = os.getcwd()
    cluster_manually(file_or_folder = cwd)
