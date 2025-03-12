#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc MLST, MLST interface for GIGAdoc                          #
#                                                                               #
#################################################################################

# 2025/02/25 Change input fasta select window to take over the directory opened previously.
# 2024/02/02 Default directory support
# 2023/05/26 mouse cursor change for link
# 2023/01/05 initial ver.

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font
import os
import os.path
import glob
import docker
import datetime
import psutil
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, jump_to_link


class createMLSTWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("MLST")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()
		if mem.total >= 8000000000: # MLST requires 8 Gbytes or more memory
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=self.select_fasta, width=14, height=3)
			buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=self.select_spades, width=14, height=3)
		else:
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=self.select_fasta, width=14, height=3, state='disable')
			buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=self.select_spades, width=14, height=3, state='disable')
		buttonSelectFasta.place(x=20, y=20)
		buttonSelectDir.place(x=20, y=90)

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', 
			command=self.select_outdir, width=14, height=3, state='normal')
		buttonOutDir.place(x=210, y=50)

		buttonDummyReview = tk.Button(self.master, text='Review input\nfiles', 
			command=self.review_files, width=14, height=3, state='disable')
		buttonDummyReview.place(x=400, y=50)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=600, y=160)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_mlst = tk.Label(self.master, text= 'Link to mlst: https://github.com/tseemann/mlst', 
			font=font.Font(size=12), fg='#0000ff')
		label_mlst.place(x=20, y=240)
		label_mlst.bind('<Button-1>', lambda e:jump_to_link('https://github.com/tseemann/mlst'))

		label_mlst_version = tk.Label(self.master, text= 'version 2.23.0', font=font.Font(size=10))
		label_mlst_version.place(x=20, y=260)

		widgets = [label_mlst]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))
		
	fasta_dic = {}
	input_dic = {} # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
	input_list = []
	dir_path = {'datadir':'', 'outdir':'', 'ref_file':''}
	dir_path['outdir'] = user_home('mlstoutdir')
	dir_list = []
	open_dir = user_home('datadir') # 2025/02/25

	def close_Window(self):
		self.master.destroy()

	def select_fasta(self):
		fTyp = [('fasta', '*.fasta'), ('fasta', '*.fa'), ('fasta', '*.fna')]
		fasta_files = tk.filedialog.askopenfilenames(parent = self.master,filetypes=fTyp, initialdir=self.open_dir) # 2025/02/25
		print(fasta_files)
		if len(fasta_files) > 0:
			for fasta in fasta_files:
				strain = os.path.splitext(os.path.basename(fasta))[0]
				dir_name = os.path.dirname(fasta)
				filename = os.path.basename(fasta)
				self.fasta_dic[strain] = [dir_name, filename, '']
				self.open_dir = dir_name # 2025/02/25
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=60)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=400, y=50)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=60)
			print(self.fasta_dic)
		else:
			print('No fasta is selected')
			return

	def select_spades(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('assemblydir'))
		print(file_path)
		fasta_files = []
		try:
			fasta_files = fasta_files + glob.glob(file_path + '/*/SPAdes/*_contigs.fasta')
			fasta_files = fasta_files + glob.glob(file_path + '/SPAdes/*_contigs.fasta')
			fasta_files = fasta_files + glob.glob(file_path + '/*_contigs.fasta')
		except:
			print('No directory is selected')
			return
		if len(fasta_files) > 0:
			for fasta in fasta_files:
				strain = os.path.splitext(os.path.basename(fasta))[0].replace('_contigs', '')
				dir_name = os.path.dirname(fasta)
				filename = os.path.basename(fasta)
				self.fasta_dic[strain] = [dir_name, filename, '']
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=60)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=400, y=50)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=60)
			print(self.fasta_dic)
		else:
			print('No fasta is selected')
			return

	def select_outdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('mlstoutdir'))
		if len(file_path) == 0:
			print(f"{self.dir_path['outdir']} is selected")
			return
		else:	
			print(file_path)
			self.dir_path['outdir'] = file_path
		label_outdir = tk.Label(self.master, text='Output dir: ' + file_path, font=font.Font(size=12))
		label_outdir.place(x=20, y=200)


	def review_files(self):
		def adapt_changes():
			i = len(self.input_dic)
			self.input_dic.clear()
			self.fasta_dic.clear()
			for record_id in range(i):
				try:
					values = tree.item(record_id, 'values')
					print(values)
					self.input_dic[values[1]] = values
				except:
					pass

		def close_Window():
			adapt_changes()
			print(self.input_dic)
			ReviewWindow.destroy()

		def delete_record(event):
			record_id = tree.focus()
			record_values = tree.item(record_id, 'values')
			if tk.messagebox.askokcancel(title='Delete confirmation', message='Delete selected record?'):
				tree.delete(record_id)
		
		def run_mlst():
			adapt_changes()
			print(self.input_dic)
			dt_now = datetime.datetime.now()
			out_file = self.dir_path['outdir'] + '/mlst_' + str(dt_now.strftime('%Y%m%d%H%M')) + '.txt'
			strains = ''
			results_dic = {}
			results_text_dic = {}

			tag = docker_tag('mlst')
			mlst_container = 'quay.io/biocontainers/mlst:' + tag
			client = docker.from_env()
			
			with open(out_file, 'w', newline='\n') as f:
				for key in self.input_dic:
					mlst_cmd = 'mlst ' + self.input_dic[key][3]
					print(self.input_dic[key])
					mlst_results = client.containers.run(mlst_container, mlst_cmd, remove=True, platform = 'linux/x86_64', 
						volumes=[self.input_dic[key][2] + ':/mnt'], working_dir='/mnt')
					f.write(mlst_results.decode('utf-8'))
					print(mlst_results.decode('utf8'))
			
			ReviewWindow.destroy()
			
		
		if len(self.fasta_dic) >= 1:
			for key in self.fasta_dic:
				self.input_dic[key] = ['fasta', key, self.fasta_dic[key][0], self.fasta_dic[key][1], self.fasta_dic[key][2]]
		print(self.input_dic)
			
		ReviewWindow = tk.Toplevel(self.master)
		ReviewWindow.geometry("1100x400+150+530")
		ReviewWindow.title("Review input files")
		tree = ttk.Treeview(ReviewWindow, columns=['Type', 'SampleID', 'dir', 'Sequence_1']) #, 'Sequence_2'])
		tree.bind("<Double-Button-1>", delete_record)
		# Setting columns
		tree.column('#0',width=0, stretch='no')
		tree.column('Type', anchor='w', width=50, stretch=True)
		tree.column('SampleID', anchor='w', width=150, stretch=True)
		tree.column('dir',anchor='w', width=500, stretch=True)
		tree.column('Sequence_1',anchor='w', width=250, stretch=True)
		#tree.column('Sequence_2', anchor='w', width=250, stretch=True)
		# Setting titles of columns
		tree.heading('#0',text='')
		tree.heading('Type', text='File type',anchor='w')
		tree.heading('SampleID', text='SampleID',anchor='w')
		tree.heading('dir', text='dir',anchor='w')
		tree.heading('Sequence_1', text='Sequence_1', anchor='w')
		#tree.heading('Sequence_2',text='Sequence_2', anchor='w')
		# Adding records
		i = 0
		for key in self.input_dic:
			tree.insert(parent='', index='end', iid=i ,values=(self.input_dic[key][0], self.input_dic[key][1], 
				self.input_dic[key][2], self.input_dic[key][3]))
			i += 1

		tree.pack(pady=50)
		buttonCancel = tk.Button(ReviewWindow, text = "Return to file selection", command=close_Window, width=18, height=3)
		buttonCancel.place(x=600, y=320)
		buttonRun = tk.Button(ReviewWindow, text = "Run MLST", command=run_mlst, width=18, height=3)
		buttonRun.place(x=300, y=320)
		label_msg1 = tk.Label(ReviewWindow, text='Double-click to delete record. To add data, return to the previous screen.', font=font.Font(size=16))
		label_msg1.place(x=50, y=280)
		
	
def main():
	root = tk.Tk()
	app = createMLSTWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

