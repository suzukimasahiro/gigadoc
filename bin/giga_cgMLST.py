#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc cgMLST, cgMLST interface for GIGAdoc                      #
#                                                                               #
#################################################################################

# 2025/03/12 Change scheme selection combo-box to display only installed schemes
# 2025/02/25 Change input fasta select window to take over the directory opened previously.
# 2023/12/14 Ver.0.1

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
from gigadoc_functions import user_home, jump_to_link, spades_contig, chk_dir
from giga_cgMLSTsettings import cgmlst_schemes, prepare_dir, cgmlst_files
from giga_cgMLSTscheme import createCgMLSTschemeWindow


class createcgMLSTWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("cgMLST")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()

		def select_combo(event):
			self.scheme = comboSelectScheme.get()
			dbdir = f"{user_home('cgMLSTdir')}/schemes/{self.scheme}" #cgmlst_files(self.scheme,'cgMLSTdir') + cgmlst_files(self.scheme, 'dbdir')
			print(self.scheme)
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=self.select_fasta, width=14, height=3, state='normal')
			buttonSelectFasta.place(x=20, y=70)
			buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=self.select_spades, width=14, height=3, state='normal')
			buttonSelectDir.place(x=20, y=140)

		def chk_db():
			print('chk_db')
					
		def get_directories():
			"""Returns a list of directories (not files) in the watched directory."""
			try:
				return sorted([d for d in os.listdir(f"{user_home('cgMLSTdir')}/schemes") 
							if os.path.isdir(os.path.join(f"{user_home('cgMLSTdir')}/schemes", d))]
							)
			except FileNotFoundError:
				return []  # Return empty if directory is missing

		def update_combobox(combo_box, last_directories):
			"""Updates the combobox if directory structure changes (only directories)."""
			current_directories = get_directories()
			if current_directories != last_directories[0]:  # Only update if there's a change
				combo_box["values"] = current_directories  # Update values
				if current_directories:
					combo_box.current(0)  # Select the first item if available
				else:
					combo_box.set("")  # Clear selection if empty
				last_directories[0] = current_directories  # Save the new state

			# Schedule the next check after 2 seconds
			self.master.after(2000, lambda: update_combobox(combo_box, last_directories))


		last_directories = ['Empty']

		if mem.total >= 8000000000: # cgMLST requires 8 Gbytes or more memory
			value = tk.StringVar()
			comboSelectScheme = ttk.Combobox(self.master, values=last_directories, state="readonly", width = 45)
			'''
			comboSelectScheme = ttk.Combobox(self.master,
								state="readonly",
								values = 
								[f for f in os.listdir(f"{user_home('cgMLSTdir')}/schemes") 
								if os.path.isdir(os.path.join(f"{user_home('cgMLSTdir')}/schemes", f))], #cgmlst_schemes('key'), #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
								textvariable = value,
								width = 45
								)
			'''
			comboSelectScheme.bind('<<ComboboxSelected>>', select_combo)
		else:
			comboSelectScheme = ttk.Combobox(self.master, state="disable", width = 45)
		comboSelectScheme.place(x=160, y=25)
		label_selectScheme = tk.Label(self.master, text='Choose scheme', font=font.Font(size=12))
		label_selectScheme.place(x=20, y=25)


		buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=self.select_fasta, width=14, height=3, state='disable')
		buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=self.select_spades, width=14, height=3, state='disable')
		buttonSelectFasta.place(x=20, y=70)
		buttonSelectDir.place(x=20, y=140)

		buttonDummyReview = tk.Button(self.master, text='Review input\nfiles', 
			command=self.review_files, width=14, height=3, state='disable')
		buttonDummyReview.place(x=210, y=100)

		def open_CgMLSTschemeWindow():
			self.newWindow = tk.Toplevel(self.master)
			self.app = createCgMLSTschemeWindow(self.newWindow)
		buttonInstallScheme = tk.Button(self.master, text = "Install\ncgMLST scheme", 
			command=open_CgMLSTschemeWindow, width=14, height=3)
		buttonInstallScheme.place(x=600, y=25)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=600, y=160)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_mlst = tk.Label(self.master, text= 'Link to chewieSnake: https://gitlab.com/bfr_bioinformatics/chewieSnake', 
			font=font.Font(size=12), fg='#0000ff')
		label_mlst.place(x=20, y=250)
		label_mlst.bind('<Button-1>', lambda e:jump_to_link('https://gitlab.com/bfr_bioinformatics/chewieSnake'))

		widgets = [label_mlst]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))
			
		update_combobox(comboSelectScheme, last_directories)
		
	fasta_dic = {}
	input_dic = {} # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
	input_list = []
	dir_path = {'datadir':'', 'outdir':'', 'ref_file':''}
	dir_list = []
	open_dir = user_home('datadir') # 2025/02/25
	scheme = ''

	def close_Window(self):
		self.master.destroy()

	def select_fasta(self):
		fTyp = [('fasta', '*.fasta'), ('fasta', '*.fa'), ('fasta', '*.fna')]
		fasta_files = filedialog.askopenfilenames(
					parent = self.master,filetypes=fTyp, initialdir=self.open_dir) # 2025/02/25
		print(fasta_files)
		if len(fasta_files) > 0:
			for fasta in fasta_files:
				strain = os.path.splitext(os.path.basename(fasta))[0]
				dir_name = os.path.dirname(fasta)
				if os.name == 'nt':
					dir_name = dir_name.replace(os.sep,'/')
				filename = os.path.basename(fasta)
				self.fasta_dic[strain] = [dir_name, filename, '']
				self.dir_list.append(dir_name)
				self.open_dir = dir_name # 2025/02/25
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=130)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=210, y=100)
			print(self.fasta_dic)
		else:
			print('No fasta is selected')
			return

	def select_spades(self):
		file_path = filedialog.askdirectory(parent = self.master, initialdir = user_home('assemblydir'))
		print(file_path)
		spades_ret = spades_contig(file_path)
		if spades_ret == 'NotFound':
			pass
		else:
			for key in spades_ret:
				self.dir_list.append(spades_ret[key][0])
			self.fasta_dic.update(spades_ret)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=60)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=210, y=100)
			print(self.fasta_dic)

	def review_files(self):
		def adapt_changes():
			i = len(self.input_dic)
			self.input_dic.clear()
			self.fasta_dic.clear()
			for record_id in range(i):
				try:
					values = tree.item(record_id, 'values')
					#print(values)
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
		
		def run_cgmlst():
			adapt_changes()
			print(self.input_dic)
			dt_now = datetime.datetime.now()
			cgmlst_dir = cgmlst_files(self.scheme, 'cgMLSTdir')
			scheme_dir = cgmlst_files(self.scheme, 'each_scheme')
			report_dir = '/' + str(dt_now.strftime('%Y%m%d%H%M'))
			chk_dir(cgmlst_dir, '/out')
			chk_dir(cgmlst_dir + '/out', scheme_dir)
			chk_dir(cgmlst_dir + '/out' + scheme_dir, report_dir)
			working_dir = '/out' + scheme_dir + report_dir
			db_dir = cgmlst_files(self.scheme, 'dbdir')
			trnfile = cgmlst_files(self.scheme, 'trndir') + '/' + cgmlst_files(self.scheme, 'trn')
			
			indir_list = []
			for key in self.input_dic:
				indir_list.append(self.input_dic[key][2])
			if os.name == 'nt':
				drive = indir_list[0][:2]
				for each in indir_list:
					if drive == each[:2]:
						pass
					else:
						messagebox.showerror('Worning!!!', 'Genome data must be on the same DRIVE on Windows.')
						return()
			mount_path = os.path.commonpath(indir_list)
			if os.name == 'nt':
				mount_path = mount_path.replace(os.sep,'/')
			print(mount_path)
			
			sample_sheet = cgmlst_dir + working_dir + '/sample.tsv'
			with open(sample_sheet, 'w') as f:
				f.write('sample\tassembly\n')
				for key in self.input_dic:
					fasta_path = self.input_dic[key][2].replace(mount_path, '/mnt')
					strain = self.input_dic[key][1]
					f.write(strain + '\t' + fasta_path + '/' + self.input_dic[key][3] + '\n')
			#print(self.input_dic)


			cgmlst_container = 'bfrbioinformatics/chewiesnake:3.2.1'
			client = docker.from_env()
			cgmlst_cmd = '/chewieSnake/chewieSnake.py ' + \
						'--sample_list /chewieSnake/analysis' + working_dir + '/sample.tsv' + \
						' --working_directory /chewieSnake/analysis' + working_dir + \
						' -t 8' + \
						' --scheme /chewieSnake/analysis' + db_dir + \
						' --prodigal /chewieSnake/analysis' + trnfile 
			if os.name == 'nt':
				uid = '0'
			else:
				uid = str(os.getuid())
			client.containers.run(cgmlst_container, cgmlst_cmd, remove=True, platform = 'linux/x86_64', 
						volumes=[cgmlst_dir + ':/chewieSnake/analysis', mount_path + ':/mnt'],
						environment=['LOCAL_USER_ID=' + uid]
						)
			
			jump_to_link('file://' + cgmlst_dir + working_dir + '/reports/cgmlst_report.html')
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
		buttonRun = tk.Button(ReviewWindow, text = "Run cgMLST", command=run_cgmlst, width=18, height=3)
		buttonRun.place(x=300, y=320)
		label_msg1 = tk.Label(ReviewWindow, text='Double-click to delete record. To add data, return to the previous screen.', font=font.Font(size=16))
		label_msg1.place(x=50, y=280)
		
	
def main():
	root = tk.Tk()
	app = createcgMLSTWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

