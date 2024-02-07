#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc SNIPPY, SNIPPY interface for GIGAdoc                      #
#                                                                               #
#################################################################################

# 2024/02/02 Ver.0.1.2 Default directory support
# 2023/05/26 Ver.0.1.1 mouse cursor change for link
# 2023/01/05 SPAdes results directory support
# 2022/12/02 Replace docker contaner from staphb to bioconda
# 2022/11/30 Ver.0.1

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
import time
import shutil
import psutil
from Bio import Phylo
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, illumina_fastq, jump_to_link


class createSnippyWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x375+50+250")
		self.master.title("SNIPPY")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()
		if mem.total >= 8000000000: # SNIPPY requires 8 Gbytes or more memory
			buttonSelectRef = tk.Button(self.master, text='Select Reference\nfile', 
			command=self.select_ref, width=14, height=3)
		else:
			buttonSelectRef = tk.Button(self.master, text='Select Reference\nfile', 
			command=self.select_ref, width=14, height=3,  state='disable')
		buttonSelectRef.place(x=20, y=80)

		buttonDummySelectFastq = tk.Button(self.master, text='Select FASTQ\nfiles', 
			command=self.select_fastq, width=14, height=3, state='disable')
		buttonDummySelectFastq.place(x=210, y=10)

		buttonDummySelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
			command=self.select_fasta, width=14, height=3, state='disable')
		buttonDummySelectFasta.place(x=210, y=80)

		buttonDummySelectFasta = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
			command=self.select_spades, width=14, height=3, state='disable')
		buttonDummySelectFasta.place(x=210, y=150)

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', 
			command=self.select_outdir, width=14, height=3, state='normal')
		buttonOutDir.place(x=400, y=80)

		buttonDummyReview = tk.Button(self.master, text='Review input\nfiles', 
			command=self.review_files, width=14, height=3, state='disable')
		buttonDummyReview.place(x=590, y=80)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=600, y=290)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_snippy = tk.Label(self.master, text= 'Link to SNIPPY: https://github.com/tseemann/snippy', 
			font=font.Font(size=12), fg='#0000ff')
		label_snippy.place(x=20, y=280)
		label_snippy.bind('<Button-1>', lambda e:jump_to_link('https://github.com/tseemann/snippy'))
		label_snpdists = tk.Label(self.master, text= 'Link to snp-dists: https://github.com/tseemann/snp-dists', 
			font=font.Font(size=12), fg='#0000ff')
		label_snpdists.place(x=20, y=305)
		label_snpdists.bind('<Button-1>', lambda e:jump_to_link('https://github.com/tseemann/snp-dists'))
		label_fasttree = tk.Label(self.master, text= 'Link to FastTree: http://www.microbesonline.org/fasttree', 
			font=font.Font(size=12), fg='#0000ff')
		label_fasttree.place(x=20, y=330)
		label_fasttree.bind('<Button-1>', lambda e:jump_to_link('http://www.microbesonline.org/fasttree'))

		widgets = [label_snippy, label_snpdists, label_fasttree]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))
		
	fastq_dic = {}
	fasta_dic = {}
	input_dic = {} # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
	input_list = []
	dir_path = {'datadir':'', 'outdir':'', 'ref_file':''}
	dir_path['outdir'] = user_home('snippydir')
	dir_list = []

	def close_Window(self):
		self.master.destroy()

	def select_ref(self):
		fTyp = [('fasta', '*.fasta'), ('fasta', '*.fa'), ('fasta', '*.fna'), ('GenBank', '*.gb'), ('GenBank', '*.gbk')]
		self.dir_path['ref_file'] = tk.filedialog.askopenfilename(parent = self.master,filetypes=fTyp, initialdir=user_home('datadir'))
		if self.dir_path['ref_file'] == '':
			print('No reference is selected')
			return
		else:	
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=170, y=90)
			
			label_ref = tk.Label(self.master, text='Reference file: ' + self.dir_path['ref_file'], font=font.Font(size=12))
			label_ref.place(x=20, y=225)

			buttonSelectFastq = tk.Button(self.master, text='Select FASTQ\nfiles', command=self.select_fastq, 
				width=14, height=3, state='normal')
			buttonSelectFastq.place(x=210, y=10)
			
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', command=self.select_fasta, 
				width=14, height=3, state='normal')
			buttonSelectFasta.place(x=210, y=80)
			
			buttonSelectFasta = tk.Button(self.master, text='SPAdes Assembly\noutput directory', command=self.select_spades, 
				width=14, height=3, state='normal')
			buttonSelectFasta.place(x=210, y=150)
			print(self.dir_path['ref_file'])

	def select_fastq(self):
		fTyp = [('fastq', '*.fastq.gz'), ('fastq', '*.fq.gz')]
		fastq_files = tk.filedialog.askopenfilenames(parent = self.master,filetypes=fTyp, initialdir=user_home('datadir'))
		print(fastq_files)
		if len(fastq_files) > 0:
			for fastq in fastq_files:
				seq_list = illumina_fastq(fastq)
				if seq_list[0] == 'Undetermined':
					pass
				else:
					self.fastq_dic[seq_list[0]] = [seq_list[1], seq_list[2], seq_list[3]]
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=90)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=550, y=90)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=590, y=80)
			print(self.fastq_dic)
		else:
			print('No fastq is selected')
			return

	def select_spades(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('assemblydir'))
		print(file_path)
		fastq_files =[]
		try:
			fastq_files = fastq_files + glob.glob(file_path + '/*/fastp/*_R1_*.fq.gz')
			fastq_files = fastq_files + glob.glob(file_path + '/fastp/*_R1_*.fq.gz')
			fastq_files = fastq_files + glob.glob(file_path + '/*_R1_*.fq.gz')
			fastq_files = fastq_files + glob.glob(file_path + '/*/fastp/*_R1_*.fastq.gz')
			fastq_files = fastq_files + glob.glob(file_path + '/fastp/*_R1_*.fastq.gz')
			fastq_files = fastq_files + glob.glob(file_path + '/*_R1_*.fastq.gz')
		except:
			print('No directory is selected')
			return
		print(fastq_files)
		if len(fastq_files) > 0:
			for fastq in fastq_files:
				seq_list = illumina_fastq(fastq)
				if seq_list[0] == 'Undetermined':
					pass
				else:
					self.fastq_dic[seq_list[0]] = [seq_list[1], seq_list[2], seq_list[3]]
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=360, y=90)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=550, y=90)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=590, y=80)
			print(self.fastq_dic)
		else:
			print('No fastq is selected')
			return

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
			label_arrow.place(x=360, y=90)
			label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
			label_arrow.place(x=550, y=90)
			buttonReview = tk.Button(self.master, text='Review input\nfiles', command=self.review_files, 
				width=14, height=3, state='normal')
			buttonReview.place(x=590, y=80)
			print(self.fasta_dic)
		else:
			print('No fasta is selected')
			return

	def select_outdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('snippydir'))
		if file_path == '':
			print('No directory is selected')
			return
		else:	
			print(file_path)
			self.dir_path['outdir'] = file_path
		label_outdir = tk.Label(self.master, text='Output dir: ' + file_path, font=font.Font(size=12))
		label_outdir.place(x=20, y=250)

	def review_files(self):
		def adapt_changes():
			i = len(self.input_dic)
			self.input_dic.clear()
			self.fastq_dic.clear()
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

		def run_snippy():
			adapt_changes()
			print(self.input_dic)
			outdir = self.dir_path['outdir']
			reffile = self.dir_path['ref_file']
			ref_basename = os.path.basename(reffile)
			shutil.copy2(reffile, outdir + '/' + ref_basename)
			runme = []
			strains = ''
			reference = ''

			with open(outdir + '/strain.list', 'w', newline='\n') as f:
				for key in self.input_dic:
					if self.input_dic[key][0] == 'FASTQ':
						f.write(self.input_dic[key][1] + '\t' + self.input_dic[key][2] + '/' + self.input_dic[key][3] + '\t' +
							self.input_dic[key][2] + '/' + self.input_dic[key][4] + '\n')
						snippy_cmd = 'snippy --outdir \'' + self.input_dic[key][1] + '\' --R1 \'/mnt/' + self.input_dic[key][3] +  \
							'\' --R2 \'/mnt/' + self.input_dic[key][4] + '\' --ref ' + ref_basename
					else:
						f.write(self.input_dic[key][1] + '\t' + self.input_dic[key][2] + '/' + self.input_dic[key][3] + '\n')
						snippy_cmd = 'snippy --outdir \'' + self.input_dic[key][1] + '\' --ctgs \'/mnt/' + self.input_dic[key][3] +  \
							'\' --ref ' + ref_basename
					runme.append([self.input_dic[key][1], self.input_dic[key][2], snippy_cmd])
					strains = strains + self.input_dic[key][1] + ' '
					reference = self.input_dic[key][1] + '/ref.fa'
			
			snippy_tag = docker_tag('SNIPPY')
			fasttree_tag = docker_tag('FastTree')
			snpdists_tag = docker_tag('snp-dists')
			snippy_container = 'quay.io/biocontainers/snippy:' + snippy_tag
			fasttree_container = 'quay.io/biocontainers/fasttree:' + fasttree_tag
			snpdists_container = 'quay.io/biocontainers/snp-dists:' + snpdists_tag
			client = docker.from_env()
			
			for each in runme: #runme = [ strain, dir, snippy_cmd]
				if os.path.isdir(outdir + '/' + each[0]):
					print(each[0], 'pass')
				else:
					volume_list = [outdir + ':/home', each[1] + ':/mnt']
					print(volume_list)
					client.containers.run(snippy_container, each[2], remove=True, volumes=volume_list, working_dir='/home')
			print('snippy-core')
			snippy_core = 'snippy-core --ref \'' + reference + '\' ' + strains
			client.containers.run(snippy_container, snippy_core, remove=True, volumes=[outdir + ':/home'], working_dir='/home')
			
			print('snp-dists')
			snpdists_cmd = 'snp-dists core.aln'
			snp_distance = client.containers.run(snpdists_container, snpdists_cmd, remove=True, 
				volumes=[outdir + ':/home'], working_dir='/home')
			with open(outdir + '/core_distance.tab', 'w', newline='\n') as f:
				f.write(snp_distance.decode('utf-8'))
			
			print('FastTree')
			fasttree_cmd = 'FastTree -gtr -nt core.aln'
			tre_file = client.containers.run(fasttree_container, fasttree_cmd, remove=True, 
				volumes=[outdir + ':/home'], working_dir='/home')
			with open(outdir + '/core.tre', 'w', newline='\n') as f:
				f.write(tre_file.decode('utf-8'))
			
			print('Tree file: ', outdir + '/core.tre')
			tree = Phylo.read(outdir + '/core.tre', 'newick')
			Phylo.draw_ascii(tree)
			
			ReviewWindow.destroy()

		
		if len(self.fastq_dic) >= 1:
			for key in self.fastq_dic:
				self.input_dic[key] = ['FASTQ', key, self.fastq_dic[key][0], self.fastq_dic[key][1], self.fastq_dic[key][2]]
		if len(self.fasta_dic) >= 1:
			for key in self.fasta_dic:
				self.input_dic[key] = ['fasta', key, self.fasta_dic[key][0], self.fasta_dic[key][1], self.fasta_dic[key][2]]
		print(self.input_dic)
			
		ReviewWindow = tk.Toplevel(self.master)
		ReviewWindow.geometry("1100x400+150+530")
		ReviewWindow.title("Review input files")
		tree = ttk.Treeview(ReviewWindow, columns=['Type', 'SampleID', 'dir', 'Sequence_1', 'Sequence_2'])
		tree.bind("<Double-Button-1>", delete_record)
		# Setting columns
		tree.column('#0',width=0, stretch='no')
		tree.column('Type', anchor='w', width=50, stretch=True)
		tree.column('SampleID', anchor='w', width=150, stretch=True)
		tree.column('dir',anchor='w', width=300, stretch=True)
		tree.column('Sequence_1',anchor='w', width=250, stretch=True)
		tree.column('Sequence_2', anchor='w', width=250, stretch=True)
		# Setting titles of columns
		tree.heading('#0',text='')
		tree.heading('Type', text='File type',anchor='w')
		tree.heading('SampleID', text='SampleID',anchor='w')
		tree.heading('dir', text='dir',anchor='w')
		tree.heading('Sequence_1', text='Sequence_1', anchor='w')
		tree.heading('Sequence_2',text='Sequence_2', anchor='w')
		# Adding records
		i = 0
		for key in self.input_dic:
			tree.insert(parent='', index='end', iid=i ,values=(self.input_dic[key][0], self.input_dic[key][1], \
			self.input_dic[key][2], self.input_dic[key][3], self.input_dic[key][4]))
			i += 1

		tree.pack(pady=50)
		buttonCancel = tk.Button(ReviewWindow, text = "Return to file selection", command=close_Window, width=18, height=3)
		buttonCancel.place(x=600, y=320)
		buttonRun = tk.Button(ReviewWindow, text = "Run SNIPPY", command=run_snippy, width=18, height=3)
		buttonRun.place(x=300, y=320)
		label_msg1 = tk.Label(ReviewWindow, text='Double-click to delete record. To add data, return to the previous screen.', 
			font=font.Font(size=16))
		label_msg1.place(x=50, y=280)
		
	
def main():
	root = tk.Tk()
	app = createSnippyWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

