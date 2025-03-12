#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#                                                                               #
#################################################################################

# 2025/03/12 Support AMRfinder option settings and other minor updates
# 2024/02/28 Fix bugs
# 2024/02/02 Default Settings, cgMLST, fastANI, and Update check support
# 2023/01/05 AMRfinder and MLST
# 2022/11/30 SPAdes and SNIPPY

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as font
from tkinter import messagebox
from datetime import datetime
from giga_spades import createSpadesWindow
from giga_snippy import createSnippyWindow
from giga_amrfinder import createAMRfinderWindow
from giga_mlst import createMLSTWindow
from giga_cgMLST import createcgMLSTWindow
from giga_fastANI import createANIWindow
from giga_defaultSetting import createSettingsWindow
from gigadoc_functions import jump_to_link, settings, system_home
import psutil
import os
import requests
import json

time_stump = '2025-03-12'

class mainwindow(tk.Frame):
	def __init__(self,master):
		super().__init__(master)
		self.pack()
		self.master.title("GIGAdoc")
		self.master.geometry("800x320+20+20")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()
		
		### Create tabs
		tab_control = ttk.Notebook(self.master)
		tab_assembly = ttk.Frame(tab_control)
		tab_control.add(tab_assembly, text='Assembly')
		tab_control.pack(expand=1, fill="both")

		tab_finder = ttk.Frame(tab_control)
		tab_control.add(tab_finder, text='Finder')
		tab_control.pack(expand=1, fill="both")

		tab_typing = ttk.Frame(tab_control)
		tab_control.add(tab_typing, text='Typing')
		tab_control.pack(expand=1, fill="both")
		
		tab_phylo = ttk.Frame(tab_control)
		tab_control.add(tab_phylo, text='Phylogeny')
		tab_control.pack(expand=1, fill="both")

		### Create frame
		frame = tk.Frame(self.master, width=800, height=120, relief=tk.GROOVE, bd=2)
		frame.propagate(False)
		frame.pack()
		
		
		
		style = ttk.Style()
		style.theme_use('default')
		style.configure('office.TButton', font=14, anchor='w')
		
		###### SPAdes #####
		if mem.total >= 16000000000: # SPAdes requires 16 Gbytes or more memory
			buttonSPAdes = ttk.Button(tab_assembly, text="SPAdes assembly", command=self.open_spades, width=18, padding=[12,20])
		else:
			buttonSPAdes = ttk.Button(tab_assembly, text="SPAdes assembly", command=self.open_spades, width=18, padding=[12,20], state='disable')
		buttonSPAdes.place(x=20, y=40)
		
		##### AMRfinder #####
		if mem.total >= 8000000000: # AMRfinder requires 8 Gbytes or more memory
			self.buttonAMRfinder = ttk.Button(tab_finder, text="AMRfinder plus", command=self.open_amrfinder, width=18, padding=[12,20])
		else:
			self.buttonAMRfinder = ttk.Button(tab_findern, text="AMRfinder plus", command=self.open_amrfinder, width=18, padding=[12,20], state='disable')
		self.buttonAMRfinder.place(x=20, y=40)

		##### MLST #####
		if mem.total >= 8000000000: # MLST requires 8 Gbytes or more memory
			self.buttonMLST = ttk.Button(tab_typing, text="MLST", command=self.open_mlst, width=18, padding=[12,20])
		else:
			self.buttonMLST = ttk.Button(tab_typing, text="MLST", command=self.open_mlst, width=18, padding=[12,20], state='disable')
		self.buttonMLST.place(x=20, y=40)

		##### fastANI #####
		if mem.total >= 8000000000: # fastANI requires 8 Gbytes or more memory
			self.buttonANI = ttk.Button(tab_typing, text="fastANI", command=self.open_ani, width=18, padding=[12,20])
		else:
			self.buttonANI = ttk.Button(tab_typing, text="fastANI", command=self.open_ani, width=18, padding=[12,20], state='disable')
		self.buttonANI.place(x=220, y=40)

		##### SNIPPY #####
		if mem.total >= 8000000000: # SNIPPY requires 8 Gbytes or more memory
			self.buttonSnippy = ttk.Button(tab_phylo, text="SNIPPY", command=self.open_snippy, width=18, padding=[12,20])
		else:
			self.buttonSnippy = ttk.Button(tab_phylo, text="SNIPPY", command=self.open_snippy, width=18, padding=[12,20], state='disable')
		self.buttonSnippy.place(x=20, y=40)

		##### cgMLST #####
		if mem.total >= 8000000000: # MLST requires 8 Gbytes or more memory
			self.buttoncgMLST = ttk.Button(tab_phylo, text="cgMLST", command=self.open_cgmlst, width=18, padding=[12,20])
		else:
			self.buttoncgMLST = ttk.Button(tab_phylo, text="cgMLST", command=self.open_cgmlst, width=18, padding=[12,20], state='disable')
		self.buttoncgMLST.place(x=220, y=40)

		##### Default settings #####
		self.buttonSettings = tk.Button(frame, text="Default Settings", command=self.open_settings, width=18, height=2)
		self.buttonSettings.place(x=20, y=10)

		##### Exit #####
		self.closebtn = tk.Button(frame, text='Exit', command=self.close_Window, width=18, height=2)
		self.closebtn.place(x=600, y=10)

		
		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_GIGAdoc = tk.Label(frame, text= 'Link to GIGAdoc: https://github.com/suzukimasahiro/gigadoc', 
			font=font.Font(size=12), fg='#0000ff')
		label_GIGAdoc.place(x=20, y=60)
		label_GIGAdoc.bind('<Button-1>', lambda e:jump_to_link('https://github.com/suzukimasahiro/gigadoc'))

		label_dockerSDK = tk.Label(frame, text= 'Link to Docker SDK for Python: https://docker-py.readthedocs.io/en/stable/index.html', 
			font=font.Font(size=12), fg='#0000ff')
		label_dockerSDK.place(x=20, y=85)
		label_dockerSDK.bind('<Button-1>', lambda e:jump_to_link('https://docker-py.readthedocs.io/en/stable/index.html'))

		widgets = [label_GIGAdoc, label_dockerSDK]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))
		

		owner = 'suzukimasahiro'
		repo = 'gigadoc'
		url = 'https://api.github.com/repos/suzukimasahiro/gigadoc'
		response = requests.get(url)
		if response.status_code == 200:
			release_info = response.json()
			latest_version = release_info['pushed_at'][:10]
			print(f"The latest version of {repo} is {latest_version}.")
		else:
			print("Failed to retrieve release information.")
	
		date1 = datetime.strptime(time_stump, '%Y-%m-%d').date()
		date2 = datetime.strptime(latest_version, '%Y-%m-%d').date()
		date_difference = date2 - date1
		if date_difference.days >= 3:
			ret = messagebox.askyesno('New version is found', 
				'Open github GIGAdoc page.')
			if ret == True:
				jump_to_link('https://github.com/suzukimasahiro/gigadoc')
			else:
				pass
		
	def open_spades(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createSpadesWindow(self.newWindow)

	def open_snippy(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createSnippyWindow(self.newWindow)

	def open_amrfinder(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createAMRfinderWindow(self.newWindow)

	def open_mlst(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createMLSTWindow(self.newWindow)

	def open_cgmlst(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createcgMLSTWindow(self.newWindow)

	def open_ani(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createANIWindow(self.newWindow)

	def open_settings(self):
		self.newWindow = tk.Toplevel(self.master)
		self.app = createSettingsWindow(self.newWindow)

	def close_Window(self):
		self.master.destroy()
		
	
def main():
	root = tk.Tk()
	app = mainwindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

