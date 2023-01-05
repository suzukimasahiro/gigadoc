#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#                                                                               #
#################################################################################

# 2023/01/05 AMRfinder and MLST
# 2022/11/30 SPAdes and SNIPPY

import tkinter as tk
from giga_spades import createSpadesWindow
from giga_snippy import createSnippyWindow
from giga_amrfinder import createAMRfinderWindow
from giga_mlst import createMLSTWindow
import psutil
import os
	
class mainwindow(tk.Frame):
	def __init__(self,master):
		super().__init__(master)
		self.pack()
		self.master.title("GIGAdoc")
		self.master.geometry("800x300+20+20")
		self.create_widgets()
		
	def create_widgets(self):
		mem = psutil.virtual_memory()
		###### SPAdes #####
		if mem.total >= 16000000000: # SPAdes requires 16 Gbytes or more memory
			buttonSPAdes = tk.Button(self.master, text="SPAdes assembly", command=self.open_spades, width=18, height=3)
		else:
			buttonSPAdes = tk.Button(self.master, text="SPAdes assembly", command=self.open_spades, width=18, height=3, state='disable')
		buttonSPAdes.place(x=20, y=20)
		
		##### SNIPPY #####
		if mem.total >= 8000000000: # SNIPPY requires 8 Gbytes or more memory
			self.buttonSnippy = tk.Button(self.master, text="SNIPPY", command=self.open_snippy, width=18, height=3)
		else:
			self.buttonSnippy = tk.Button(self.master, text="SNIPPY", command=self.open_snippy, width=18, height=3, state='disable')
		self.buttonSnippy.place(x=200, y=20)

		##### AMRfinder #####
		if mem.total >= 8000000000: # AMRfinder requires 8 Gbytes or more memory
			self.buttonAMRfinder = tk.Button(self.master, text="AMRfinder plus", command=self.open_amrfinder, width=18, height=3)
		else:
			self.buttonAMRfinder = tk.Button(self.master, text="AMRfinder plus", command=self.open_amrfinder, width=18, height=3, state='disable')
		self.buttonAMRfinder.place(x=380, y=20)

		##### MLST #####
		if mem.total >= 8000000000: # MLST requires 8 Gbytes or more memory
			self.buttonMLST = tk.Button(self.master, text="MLST", command=self.open_mlst, width=18, height=3)
		else:
			self.buttonMLSTfinder = tk.Button(self.master, text="MLST", command=self.open_mlst, width=18, height=3, state='disable')
		self.buttonMLST.place(x=560, y=20)

		##### Exit #####
		self.closebtn = tk.Button(self.master, text='Exit', command=self.close_Window, width=18, height=3)
		self.closebtn.place(x=20, y=180)
		
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

	def close_Window(self):
		self.master.destroy()
	
def main():
	root = tk.Tk()
	app = mainwindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

