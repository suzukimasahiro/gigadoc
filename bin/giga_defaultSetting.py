#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc default directory setting panel                           #
#                                                                               #
#################################################################################

# 2024/02/05

import tkinter as tk
from tkinter import filedialog
import tkinter.font as font
import os
import os.path
import json
from gigadoc_functions import system_home, user_home, settings, update_settings, is_valid_email, chk_dir


class createSettingsWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("GIGAdoc settings")
		self.create_widgets()

	def create_widgets(self):

		def push_done():
			email = Email_box.get()
			if is_valid_email(email):
				self.settings['email'] = email
			self.close_Window_done()

		buttonDataDir = tk.Button(self.master, text='Select Data\n directory', 
			command=self.select_datadir, width=14, height=3)
		buttonDataDir.place(x=20, y=15)

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', 
			command=self.select_outdir, width=14, height=3)
		buttonOutDir.place(x=210, y=15)

		buttoncgMLSTDir = tk.Button(self.master, text='Select cgMLST\ndirectory', 
			command=self.select_cgmlstdir, width=14, height=3)
		buttoncgMLSTDir.place(x=400, y=15)

		buttonDbDir = tk.Button(self.master, text='Select Database\ndirectory', 
			command=self.select_dbdir, width=14, height=3)
		buttonDbDir.place(x=590, y=15)

		label_email = tk.Label(self.master, text='E-mail:', font=font.Font(size=12))
		label_email.place(x=20, y=95)
		Email_box = tk.Entry(self.master, width=38)
		Email_box.insert(0, user_home('email'))
		Email_box.place(x=90, y=95)

		buttonDone = tk.Button(self.master, text = "Done", 
			command=push_done, width=14, height=3)
		buttonDone.place(x=600, y=220)

		buttonCancel = tk.Button(self.master, text = "Cancel", 
			command=self.close_Window_cancel, width=14, height=3)
		buttonCancel.place(x=410, y=220)

		label_dir = tk.Label(self.master, text='Data dir: ' + self.settings['datadir'], font=font.Font(size=12))
		label_dir.place(x=20, y=130)
		label_dir = tk.Label(self.master, text='Output dir: ' + self.settings['outdir'], font=font.Font(size=12))
		label_dir.place(x=20, y=150)
		label_dir = tk.Label(self.master, text='cgMLST dir: ' + self.settings['cgMLSTdir'], font=font.Font(size=12))
		label_dir.place(x=20, y=170)
		label_dir = tk.Label(self.master, text='Database dir: ' + self.settings['dbdir'], font=font.Font(size=12))
		label_dir.place(x=20, y=190)

	settings = settings()

	def close_Window_done(self):
		update_settings(self.settings['datadir'], 
						self.settings['outdir'], 
						self.settings['cgMLSTdir'], 
						self.settings['dbdir'], 
						self.settings['email'])
		self.master.destroy()

	def close_Window_cancel(self):
		self.master.destroy()

	def select_datadir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = self.settings['datadir'])
		if file_path == '' or file_path == ():
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.settings['datadir'] = file_path
		label_dir = tk.Label(self.master, text='Data dir: ' + file_path + '                          ', 
							font=font.Font(size=12))
		label_dir.place(x=20, y=130)

	def select_outdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = self.settings['outdir'])
		if file_path == '' or file_path == ():
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.settings['outdir'] = file_path
		label_dir = tk.Label(self.master, text='Output dir: ' + file_path + '                          ', 
							font=font.Font(size=12))
		label_dir.place(x=20, y=150)

	def select_cgmlstdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = self.settings['cgMLSTdir'])
		if file_path == '' or file_path == ():
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.settings['cgMLSTdir'] = file_path
		label_dir = tk.Label(self.master, text='cgMLST dir: ' + file_path + '                          ', 
							font=font.Font(size=12))
		label_dir.place(x=20, y=70)

	def select_dbdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = self.settings['dbdir'])
		if file_path == '' or file_path == ():
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.settings['dbdir'] = file_path
		label_dir = tk.Label(self.master, text='Database dir: ' + file_path + '                          ', 
							font=font.Font(size=12))
		label_dir.place(x=20, y=190)
	
def main():
	root = tk.Tk()
	app = createSettingsWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

