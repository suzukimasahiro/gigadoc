#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc SPAdes, SPAdes assembler interface for GIGAdoc            #
#                                                                               #
#################################################################################

# 2024/10/23 Fix SPAdes directory permission error on Linux
# 2024/02/02 Calculating coverage and Default directory support
# 2023/12/18 Default dir setting support and Coverage output
# 2023/05/26 mouse cursor change for link
# 2023/01/05 Trimming bad contigs and save contigs.fasta with strain name
# 2022/11/30 test ver.

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
import psutil
import json
from Bio import SeqIO
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, illumina_fastq, jump_to_link

class createSpadesWindow(tk.Frame):
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x525+50+300")
		self.master.title("SPAdes assembly")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()
		if mem.total >= 16000000000: # SPAdes requires 16 Gbytes or more memory
			buttonSelectFastq = tk.Button(self.master, text='Select FASTQ\ndirectory', \
			command=self.select_fastq, width=14, height=3)
		else:
			buttonSelectFastq = tk.Button(self.master, text='Select FASTQ\ndirectory', \
			command=self.select_fastq, width=14, height=3, state='disable')
		buttonSelectFastq.place(x=20, y=20)

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', 
								command=self.select_outdir, width=14, height=3, state='normal')
		buttonOutDir.place(x=210, y=20)

		buttonDummyReview = tk.Button(self.master, text='Review Files', width=14, height=3, state='disable')
		buttonDummyReview.place(x=400, y=20)

		buttonDummyRunSpades = tk.Button(self.master, text='Run Spades', width=14, height=3, state='disable')
		buttonDummyRunSpades.place(x=600, y=20)

		buttonCancel = tk.Button(self.master, text = "Close", command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=600, y=430)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_fastp = tk.Label(self.master, text= 'Link to fastp: https://github.com/OpenGene/fastp', 
			font=font.Font(size=12), fg='#0000ff')
		label_fastp.place(x=20, y=455)
		label_fastp.bind('<Button-1>', lambda e:jump_to_link('https://github.com/OpenGene/fastp'))
		label_spades = tk.Label(self.master, text= 'Link to SPAdes: https://github.com/ablab/spades', 
			font=font.Font(size=12), fg='#0000ff')
		label_spades.place(x=20, y=480)
		label_spades.bind('<Button-1>', lambda e:jump_to_link('https://github.com/ablab/spades'))

		widgets = [label_fastp, label_spades]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))

	fastq_list = []
	dir_path = {'fastq':'', 'outdir':''}
	dir_path['outdir'] = user_home('assemblydir')
	
	def close_Window(self):
		self.fastq_list.clear()
		self.dir_path.clear()
		self.master.destroy()
		
	def select_fastq(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('datadir'))
		print(file_path)
		if file_path == '':
			print('No directory is selected')
			return
		else:	
			files = glob.glob(file_path + "/*R1*.fastq.gz")
			for fastq in files:
				seq_list = illumina_fastq(fastq)
				if seq_list[0] == 'Undetermined':
					pass
				else:
					self.fastq_list.append([seq_list[0], seq_list[2], seq_list[3]])
					if os.path.isfile(file_path + '/' + self.fastq_list[-1][2]):
						print(self.fastq_list[-1][2], 'ok')
					else:
						print(self.fastq_list[-1][2], 'Not Found')
			self.dir_path['fastq'] = file_path
		label_fastqdir = tk.Label(self.master, text='Fastq dir: ' + file_path, font=font.Font(size=12))
		label_fastqdir.place(x=20, y=360)
		label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
		label_arrow.place(x=175, y=30)
		buttonReviewFiles = tk.Button(self.master, text='Review Files', command=self.review_files, width=14, height=3, state='normal')
		buttonReviewFiles.place(x=400, y=20)
		label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
		label_arrow.place(x=360, y=30)
		buttonDummyFastq = tk.Button(self.master, text='Select FASTQ\ndirectory', command=self.select_fastq, width=14, height=3, state='disable')
		buttonDummyFastq.place(x=20, y=20)
		
	def select_outdir(self):
		file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('assemblydir'))
		if len(file_path) == 0:
			print(f"{self.dir_path['outdir']} is selected")
			return
		else:	
			print(file_path)
			self.dir_path['outdir'] = file_path
		label_fastqdir = tk.Label(self.master, text='Output dir: ' + file_path, font=font.Font(size=12))
		label_fastqdir.place(x=20, y=385)
		
	def review_files(self):
		def delete_record(event):
			record_id = tree.focus()
			record_values = tree.item(record_id, 'values')
			if tk.messagebox.askokcancel(title='Delete confirmation', message='Delete selected record?'):
				tree.delete(record_id)
		
		def adapt_changes():
			i = len(self.fastq_list)
			self.fastq_list.clear()
			for record_id in range(i):
				try:
					values = tree.item(record_id, 'values')
					print(values)
					self.fastq_list.append(values)
				except:
					pass
			print(self.fastq_list)

		def run_spades():
			adapt_changes()
			data_dir = self.dir_path['fastq']
			out_dir = self.dir_path['outdir']

			fastp_tag = docker_tag('fastp')
			spades_tag = docker_tag('SPAdes')
			fastp_container = 'quay.io/biocontainers/fastp:' + fastp_tag
			spades_container ='quay.io/biocontainers/spades:' + spades_tag
			client = docker.from_env()

			for line in self.fastq_list:
				print(datetime.datetime.now())
				strain = line[0]
				read1 = line[1]
				read2 = line [2]
				print(strain)
				if os.path.exists(out_dir + '/' + strain):
					pass
				else:
					os.mkdir(out_dir + '/' + strain)
				
				### fastp ###
				fastp_dir = out_dir + '/' + strain + '/fastp'
				if os.path.exists(fastp_dir):
					print('fastp: pass')
				else:
					print(strain, 'Run fastp')
					os.mkdir(fastp_dir)
					fastp_cmd = 'fastp -i /mnt/' + read1 + ' -I /mnt/' + read2 + \
					' -o ' + strain + '_R1_fastp.fastq.gz -O ' + strain + '_R2_fastp.fastq.gz' + \
					' --trim_poly_g --low_complexity_filter -Y 50 -h ' + strain + '.html -j ' + strain + '.json'
					label_run = tk.Label(self.master, text= strain + ': fastq trimming by fastp', font=font.Font(size=12))
					label_run.place(x=20, y=410)
					volume_list = [fastp_dir + ':/home', data_dir + ':/mnt']
					client.containers.run(fastp_container, fastp_cmd, remove=True, platform = 'linux/x86_64', 
											volumes=volume_list, working_dir='/home')
				with open(fastp_dir + '/' + strain + '.json', 'r')as f:
					fastp_dic = json.load(f)
					total_bases = float(fastp_dic["summary"]["after_filtering"]["total_bases"])

				### SPAdes ###
				if os.path.exists(out_dir + '/' + strain + '/SPAdes'):
					print('SPAdes: pass')
				else:
					print(strain, 'Run SPAdes')
					label_run = tk.Label(self.master, text= strain + ': assemble by SPAdes', font=font.Font(size=12))
					label_run.place(x=20, y=435)
					volume_list = [fastp_dir + ':/mnt', out_dir + '/' + strain + ':/home']
					spades_cmd = 'spades.py -o /home/SPAdes --pe1-1 ' + strain + '_R1_fastp.fastq.gz \
					--pe1-2 ' + strain + '_R2_fastp.fastq.gz'
					client.containers.run(spades_container, spades_cmd, remove=True, platform = 'linux/x86_64', 
										volumes=volume_list, working_dir='/mnt')
					chmod_cmd = 'chmod a+w /home/SPAdes'
					client.containers.run(spades_container, chmod_cmd, remove=True, platform = 'linux/x86_64', 
										volumes=volume_list, working_dir='/mnt')
					##### Change "SPAdes directory" permission to writable 24/10/23 #####
				
					### Discard waste contigs and check genone length ###
					contig_file = out_dir + '/' + strain + '/SPAdes/' + 'contigs.fasta'
					output_file = out_dir + '/' + strain + '/SPAdes/' + strain + '_contigs.fasta'
					coverage_file = out_dir + '/' + strain + '/SPAdes/' + strain + '_coverage.txt'
					outf = open(output_file, 'w', newline='\n')   ##### Permission problem is remaining on Linux #####
					genome_length = 0
					for each_seq in SeqIO.parse(contig_file, 'fasta'):
						seq_id = each_seq.id.split('_')
						#print(seq_id)
						if int(seq_id[3]) >= 200 and float(seq_id[5]) >= 2:
							length = len(each_seq.seq)
							if length <= 3000:
								nuc_a = each_seq.seq.count('A')
								nuc_t = each_seq.seq.count('T')
								nuc_g = each_seq.seq.count('G')
								nuc_c = each_seq.seq.count('C')
								dominant = max([nuc_a, nuc_c, nuc_g, nuc_t])
								print('A:', nuc_a, '\tT:', nuc_t, '\tG:', nuc_g, '\tC:', nuc_c)
								if dominant / length > 0.95:
									print('DISCARD')
								else:
									SeqIO.write(each_seq, outf, 'fasta')
									print('write')
									genome_length = genome_length + length
							else:
								SeqIO.write(each_seq, outf, 'fasta')
								print('write')
								genome_length = genome_length + length
						else:
							print('DISCARD')
					outf.close()
					with open(coverage_file, 'w') as f:
						f.write('Genome size\t' + str(genome_length) + '\n')
						f.write('Total Reads\t' + str(total_bases) + '\n')
						f.write('Coverage\t' + str(round(total_bases / genome_length)) + '\n')


			print(datetime.datetime.now())
			buttonDummyRunSpades = tk.Button(self.master, text='Run Spades', width=14, height=3, state='disable')
			buttonDummyRunSpades.place(x=600, y=20)
			label_run = tk.Label(self.master, text = 'Assemble complete!', font=font.Font(size=12))
			label_run.place(x=20, y=410)
			self.fastq_list.clear()
			self.dir_path.clear()
		
		tree = ttk.Treeview(self.master, columns=['SampleID', 'Read_1', 'Read_2'])
		tree.bind("<Double-Button-1>", delete_record)
		# Setting columns
		tree.column('#0',width=0, stretch='no')
		tree.column('SampleID', anchor='w', width=100, stretch=True)
		tree.column('Read_1',anchor='w', width=300, stretch=True)
		tree.column('Read_2', anchor='w', width=300, stretch=True)
		# Setting titles of columns
		tree.heading('#0',text='')
		tree.heading('SampleID', text='SampleID',anchor='w')
		tree.heading('Read_1', text='Read_1', anchor='w')
		tree.heading('Read_2',text='Read_2', anchor='w')
		# Adding records
		i = 0
		for each in self.fastq_list:
			tree.insert(parent='', index='end', iid=i ,values=(each[0], each[1], each[2]))
			i += 1
		tree.pack(pady=115)
		label_arrow = tk.Label(self.master, text='→', font=font.Font(size=20))
		label_arrow.place(x=555, y=30)
		buttonDummyReview = tk.Button(self.master, text='Review Files', width=14, height=3, state='disable')
		buttonDummyReview.place(x=400, y=20)
		buttonRunSpades = tk.Button(self.master, text='Run Spades', command=run_spades, width=14, height=3, state='normal')
		buttonRunSpades.place(x=600, y=20)


	def print_fastq(self):
		print(self.fastq_list)
		print(self.dir_path)

		
def main():
	root = tk.Tk()
	app = createSpadesWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

