#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc AMRfinder, AMRfinder interface for GIGAdoc                #
#                                                                               #
#################################################################################

# 2024/02/02 Default directory support
# 2023/06/09 Fix results order to that of input
# 2023/05/26 mouse cursor change for link
# 2023/01/05 Initial ver.

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
import copy
import psutil
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, jump_to_link
from run_amrfinder import amr_summary, amr_resultsfile, amr2excel, amr2txt


class createAMRfinderWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("NCBI AMRfinder plus")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()
		if mem.total >= 8000000000: # AMRfinder requires 8 Gbytes or more memory
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

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', command=self.select_outdir, 
			width=14, height=3, state='normal')
		buttonOutDir.place(x=210, y=50)

		buttonDummyReview = tk.Button(self.master, text='Review input\nfiles', 
			command=self.review_files, width=14, height=3, state='disable')
		buttonDummyReview.place(x=400, y=50)

		buttonUpdate = tk.Button(self.master, text = "Update Database", 
			command=self.updatedb, width=14, height=3)
		buttonUpdate.place(x=600, y=50)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=600, y=160)
		
		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_amrfinder = tk.Label(self.master, text= 'Link to AMRFinderPlus: https://github.com/ncbi/amr/wiki', 
			font=font.Font(size=12), fg='#0000ff')
		label_amrfinder.place(x=20, y=250)
		label_amrfinder.bind('<Button-1>', lambda e:jump_to_link('https://github.com/ncbi/amr/wiki'))

		widgets = [label_amrfinder]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))

	fasta_dic = {}
	input_dic = {} # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
	input_list = []
	dir_path = {'datadir':'', 'outdir':'', 'ref_file':''}
	dir_path['outdir'] = user_home('amrfinderdir')
	dir_list = []

	def close_Window(self):
		self.master.destroy()

	def select_fasta(self):
		fTyp = [('fasta', '*.fasta'), ('fasta', '*.fa'), ('fasta', '*.fna')]
		fasta_files = tk.filedialog.askopenfilenames(parent = self.master,filetypes=fTyp, initialdir=user_home('datadir'))
		print(fasta_files)
		if len(fasta_files) > 0:
			for fasta in fasta_files:
				strain = os.path.splitext(os.path.basename(fasta))[0]
				dir_name = os.path.dirname(fasta)
				filename = os.path.basename(fasta)
				self.fasta_dic[strain] = [dir_name, filename, '']
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=60)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=60)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=400, y=50)
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
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=60)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=400, y=50)
			print(self.fasta_dic)
		else:
			print('No fasta is selected')
			return

	def select_outdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('amrfinderdir'))
		if file_path == '':
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.dir_path['outdir'] = file_path
		label_outdir = tk.Label(self.master, text='Output dir: ' + file_path, font=font.Font(size=12))
		label_outdir.place(x=20, y=200)
		label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
		label_arrow.place(x=360, y=60)
		buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
			width=14, height=3, state='normal')
		buttonReview.place(x=400, y=50)

	def updatedb(self):
		print('update AMRfinder database')
		idir = user_home('amrfinderdbdir')
		tag = docker_tag('AMRfinder')
		if os.path.isdir(idir + '/' + tag):
			pass
		else:
			os.mkdir(idir + '/' + tag)
		amrfinder_container = 'quay.io/biocontainers/ncbi-amrfinderplus:' + tag
		dbdir = idir + '/' + tag
		client = docker.from_env()
		client.containers.run(amrfinder_container, 'amrfinder -u', remove=True, volumes=[dbdir + ':/usr/local/share'])

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
		
		def run_amrfinder():
			adapt_changes()
			print(self.input_dic)
			dt_now = datetime.datetime.now()
			out_name = self.dir_path['outdir'] + '/amrfinder_' + str(dt_now.strftime('%Y%m%d%H%M'))
			strains = ''
			results_dic = {}
			results_text_dic = {}
			strain_list = [] # 2023/6/9

			tag = docker_tag('AMRfinder')
			dbdir = user_home('amrfinderdbdir') + '/' + tag
			amrfinder_container = 'quay.io/biocontainers/ncbi-amrfinderplus:' + tag
			client = docker.from_env()
			
			if os.path.isdir(dbdir + '/amrfinderplus/data/latest'):
				pass
			else:
				self.updatedb()
			
			for key in self.input_dic:
				strain_list.append(key)
				amrfinder_cmd = 'amrfinder -n ' + self.input_dic[key][3] + ' -i 0.7 --threads 4'
				print(amrfinder_cmd)
				print(self.input_dic[key])
				amr_results = client.containers.run(amrfinder_container, amrfinder_cmd, remove=True, 
					volumes=[self.input_dic[key][2] + ':/mnt', dbdir + ':/usr/local/share'], working_dir='/mnt')
				amr_list = amr_results.decode('utf8').rstrip().split("\n")
				results_list = []
				for amr_line in amr_list:
					amr_line_list = amr_line.split('\t')
					if amr_line_list[0] != 'Protein identifier':
						results_list.append(amr_summary(amr_line))
				print(results_list)
				results_dic[key]= copy.copy(results_list)
				results_text_dic[key] = amr_results.decode('utf8')
				results_list.clear()
			print(results_dic)
			amr2txt('', results_text_dic, strain_list, out_name) # 2023/6/9 add "strain_list"
			amr2excel(results_dic, out_name, strain_list) # 2023/6/9 add "strain_list"
			
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
		buttonRun = tk.Button(ReviewWindow, text = "Run AMRfinder", command=run_amrfinder, width=18, height=3)
		buttonRun.place(x=300, y=320)
		label_msg1 = tk.Label(ReviewWindow, text='Double-click to delete record. To add data, return to the previous screen.', font=font.Font(size=16))
		label_msg1.place(x=50, y=280)
		
	
def main():
	root = tk.Tk()
	app = createAMRfinderWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

