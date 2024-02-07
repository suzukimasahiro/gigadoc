#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc fastANI, ANI interface for GIGAdoc                        #
#                                                                               #
#################################################################################

# 2024/02/07 Ver.0.1

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import tkinter.font as font
import os
import os.path
import glob
import uuid
import docker
import datetime
import psutil
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, jump_to_link, is_valid_email
import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Blast import NCBIWWW, NCBIXML
from Bio import Entrez
import urllib.request
import gzip
import shutil


class createANIWindow(tk.Frame):
	fasta_dic = {}
	input_dic = {} # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
	input_list = []
	dir_path = {'datadir':'', 'outdir':'', 'ref_file':''}
	dir_path['outdir'] = user_home('anioutdir')
	dir_list = []
	email = ''
	manual_ref = 'NA'
	use_db = ''

	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("fastANI")
		self.create_widgets()

	def create_widgets(self):
		mem = psutil.virtual_memory()

		def push_done():
			self.use_db = variable.get()
			self.email = Email_box.get()
			if is_valid_email(self.email):
				self.review_files()
			else:
				messagebox.showerror('ERROR', 'Enter E-mail address')

		def select_fasta():
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
				label_arrow.place(x=170, y=50)
				label_arrow2 = tk.Label(self.master, text='→', font=font.Font(size=20))
				label_arrow2.place(x=360, y=50)
				label_arrow3 = tk.Label(self.master, text='→', font=font.Font(size=20))
				label_arrow3.place(x=550, y=50)
				buttonReview = tk.Button(self.master, text='Review input\nfiles', command=push_done, 
					width=14, height=3, state='normal')
				buttonReview.place(x=590, y=40)
				print(self.fasta_dic)
			else:
				print('No fasta is selected')
				return

		def select_spades():
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
				label_arrow.place(x=170, y=50)
				label_arrow2 = tk.Label(self.master, text='→', font=font.Font(size=20))
				label_arrow2.place(x=360, y=50)
				label_arrow3 = tk.Label(self.master, text='→', font=font.Font(size=20))
				label_arrow3.place(x=550, y=50)
				buttonReview = tk.Button(self.master, text='Review input\nfiles', command=push_done, 
					width=14, height=3, state='normal')
				buttonReview.place(x=590, y=40)
				print(self.fasta_dic)
			else:
				print('No fasta is selected')
				return

		def select_ref():
			fTyp = [('fasta', '*.fasta'), ('fasta', '*.fa'), ('fasta', '*.fna')]
			self.manual_ref = tk.filedialog.askopenfilename(parent = self.master,filetypes=fTyp, 
																		initialdir=user_home('refseqdir'))
			if self.manual_ref == '':
				self.manual_ref = 'NA'
			elif self.manual_ref not in ('','NA'):
				self.dir_path['ref_file'] = self.manual_ref
				label_ref = tk.Label(self.master, text='Reference: ' + self.dir_path['ref_file'], font=font.Font(size=10))
				label_ref.place(x=20, y=165)
				print(f"Reference file is {self.dir_path['ref_file']}")
			return

		def select_outdir():
			file_path = tk.filedialog.askdirectory(parent = self.master, initialdir = user_home('anioutdir'))
			if file_path == '':
				print('No directory is selected')
				return
			else:	
				print(file_path)
				self.dir_path['outdir'] = file_path
				
		def get_nt_prok():
			if messagebox.askyesno('Download db files takes a time.','Are you sure to get nt_prok database?'):
				client = docker.from_env()
				blast_container = f"quay.io/biocontainers/blast:{docker_tag('blast')}"
				client.containers.run(blast_container, 'update_blastdb.pl --decompress nt_prok', remove=True, 
						volumes=[f"{user_home('blastdbdir')}:/home"], working_dir='/home')
				

		label_email = tk.Label(self.master, text='E-mail:', font=font.Font(size=12))
		label_email.place(x=20, y=190)
		Email_box = tk.Entry(self.master, width=38)
		Email_box.insert(0, user_home('email'))
		Email_box.place(x=90, y=190)

		if mem.total >= 8000000000: # fastANI requires 8 Gbytes or more memory
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=select_fasta, width=14, height=3)
			buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=select_spades, width=14, height=3)
		else:
			buttonSelectFasta = tk.Button(self.master, text='Select fasta\nfiles', 
				command=select_fasta, width=14, height=3, state='disable')
			buttonSelectDir = tk.Button(self.master, text='SPAdes Assembly\noutput directory', 
				command=select_spades, width=14, height=3, state='disable')
		buttonSelectFasta.place(x=20, y=20)
		buttonSelectDir.place(x=20, y=90)

		buttonRef = tk.Button(self.master, text='Select\nReference Genome\n(Optional)', 
								command=select_ref, width=14, height=3, state='normal')
		buttonRef.place(x=210, y=40)
		label_ref1 = tk.Label(self.master, 
			text="The system will automatically set a suitable reference, but expect a delay.", font=font.Font(size=10), anchor=tk.W)
		#label_ref2 = tk.Label(self.master, text="but expect a delay.", font=font.Font(size=10), anchor=tk.W)
		label_ref1.place(x=200, y=110)
		#label_ref2.place(x=210, y=128)

		buttonOutDir = tk.Button(self.master, text='Select Output\ndirectory', 
			command=select_outdir, width=14, height=3, state='normal')
		buttonOutDir.place(x=400, y=40)

		buttonDummyReview = tk.Button(self.master, text='Review input\nfiles', 
			command=push_done, width=14, height=3, state='disable')
		buttonDummyReview.place(x=590, y=40)

		variable = tk.StringVar()
		comboSelectDB = ttk.Combobox(self.master,
							state="readonly",
							values = ['online', 'local'],
							textvariable = variable,
							width = 10
							)
		comboSelectDB.place(x=395, y=135)
		label_combo = tk.Label(self.master, text='BLAST search location:', font=font.Font(size=12))
		label_combo.place(x=200, y=135)



		buttonGetDB = tk.Button(self.master, text='Get/Update\nnt_prok blast db\n(Optional)', 
			command=get_nt_prok, width=14, height=3, state='normal')
		buttonGetDB.place(x=20, y=225)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=620, y=200)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_ani = tk.Label(self.master, text= 'Link to fastANI: https://github.com/ParBLiSS/FastANI', 
			font=font.Font(size=12), fg='#0000ff')
		label_ani.place(x=190, y=230)
		label_ani.bind('<Button-1>', lambda e:jump_to_link('https://github.com/ParBLiSS/FastANI'))

		label_ddh = tk.Label(self.master, text= 'Try digital DDH. Link to TYGS/GGDC', 
			font=font.Font(size=12), fg='#0000ff')
		label_ddh.place(x=190, y=255)
		label_ddh.bind('<Button-1>', lambda e:jump_to_link('https://ggdc.dsmz.de/'))

		widgets = [label_ani, label_ddh]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))


	def close_Window(self):
		self.master.destroy()

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
		
		def run_ani():
			def extract_sequence_range(multifasta_file, start, end):
				"""Extract a sequence range from the first sequence in a multi-FASTA file and print it."""
				with open(multifasta_file, "r") as infile:
					for record in SeqIO.parse(infile, "fasta"):
						if len(record.seq) > 100000:
							sub_sequence = record.seq[start-1:end]  # Extract the desired range
							return(sub_sequence)
						#break  # We only want the first sequence

			def extract_species_name(title):
				"""Extract species name from the title using various strategies."""
				# Try extracting using square brackets (common in BLAST titles)
				match = re.search(r'\[(.*?)\]', title)
				if match:
					return match.group(1)
			
				# Try extracting based on common patterns (genus and species names)
				match = re.search(r'\b(\w+ \w+)', title)
				if match:
					return match.group(1)
			
				# Fallback: Return the entire title or a part of it
				return title.split('|')[4] if '|' in title else title

			def local_blast(sequence):
				print("Local BLAST search.")
				save_seq = SeqRecord(Seq(sequence), id = 'query_seq')
				qfas = uuid.uuid4()
				SeqIO.write(save_seq, f"{user_home('anioutdir')}/{qfas}", 'fasta')
				client = docker.from_env()
				blast_container = f"quay.io/biocontainers/blast:{docker_tag('blast')}"
				blast_cmd = f"blastn -db /mnt/nt_prok -query {qfas} -out {qfas}.xml -outfmt 5 -num_threads 4"
				blast_results = client.containers.run(blast_container, blast_cmd, remove=True, 
						volumes=[f"{user_home('blastdbdir')}:/mnt", f"{user_home('anioutdir')}:/home"], working_dir='/home')
				with open(f"{user_home('anioutdir')}/{qfas}.xml") as result_handle:
					blast_records = NCBIXML.parse(result_handle)
					try:
						for blast_record in blast_records:
							for alignment in blast_record.alignments:
								for hsp in alignment.hsps:
									title = alignment.title
									species_name = extract_species_name(title)
									return(species_name, qfas)
					except:
						species_name = "NotFound"
				species_name = "NotFound"
				return(species_name)

			def online_blast(sequence):
				print("Online BLAST search... (this might take a while)")
				result_handle = NCBIWWW.qblast("blastn", "nt", sequence)
				blast_record = NCBIXML.read(result_handle)
				try:
					for alignment in blast_record.alignments:
						for hsp in alignment.hsps:
							if hsp.expect < 0.01:  # Using a threshold for E-value
								title = alignment.title
								species_name = extract_species_name(title)
								return species_name
				except:
					return "NotFound"
				return "NotFound"
				
			def blast_sequence(sequence):
				print("Performing BLAST search.")
				if os.path.isfile(f"{user_home('blastdbdir')}/nt_prok.00.nhr") and self.use_db == 'local':
					"""Perform a local BLAST search of the given sequence."""
					species_name, qfas = local_blast(sequence)
				elif os.path.isfile(f"{user_home('blastdbdir')}/nt_prok.00.nhr") == False and self.use_db == 'local':
					messagebox.showinfo('Warning!', 'Please download the nt_prok database before using the local BLAST search.\nNote that species searches are conducted online.')
					"""Perform a online BLAST search of the given sequence."""
					species_name = online_blast(sequence)
				else:
					"""Perform a online BLAST search of the given sequence."""
					species_name = online_blast(sequence)
				return(species_name, qfas)
			
			def search_reference_genome_assembly_id(species):
				"""Search for the assembly ID of the reference genome for the specified species."""
				Entrez.email = self.email
				query = f"{species}[Organism] AND (\"reference genome\"[Title] OR \"representative genome\"[Title])"
				handle = Entrez.esearch(db="assembly", term=query, retmax=10)
				record = Entrez.read(handle)
				handle.close()
				assembly_ids = record["IdList"]
				return assembly_ids[0] if assembly_ids else None
			
			def fetch_genome_summary(assembly_id):
				"""Fetch the summary of the genome assembly to get the FTP link."""
				handle = Entrez.esummary(db="assembly", id=assembly_id)
				summary = Entrez.read(handle)
				handle.close()
				return summary['DocumentSummarySet']['DocumentSummary'][0]['FtpPath_RefSeq']
			
			def download_genome(ftp_path, compressed_file, extracted_file):
				"""Download and extract the genome file from the FTP path."""
				ftp_path_genome = ftp_path.replace("ftp://", "https://") + '/' + ftp_path.split('/')[-1] + '_genomic.fna.gz'
				urllib.request.urlretrieve(ftp_path_genome, compressed_file)
			
				# Extracting the gzipped file
				with gzip.open(compressed_file, 'rb') as f_in:
					with open(extracted_file, 'wb') as f_out:
						shutil.copyfileobj(f_in, f_out)
			
				print(f"Genome downloaded and extracted to {extracted_file}")
			
			def species_search(multifasta_file, refseqdir):
				sequence = extract_sequence_range(multifasta_file, 500, 1500)
				#result_handle = blast_sequence(sequence)
				#species_name = parse_blast_result(result_handle)
				species_name, qfas = blast_sequence(sequence)
				if species_name == 'NotFound':
					return('NotFound', 'NoFile')
				else:
					print(f"Species identified: {species_name}")
			
				assembly_id = search_reference_genome_assembly_id(species_name)
				if assembly_id:
					print(f"Found Reference Assembly ID for {species_name}: {assembly_id}")
					ftp_path = fetch_genome_summary(assembly_id)
					print(f"FTP Path for genome: {ftp_path}")
				
					# Downloading and extracting the genome
					compressed_file = f"{refseqdir}/{species_name.replace(' ', '_')}_genome.fna.gz"
					extracted_file = f"{refseqdir}/{species_name.replace(' ', '_')}_genome.fna"
					if os.path.isfile(extracted_file):
						print(f"Found {extracted_file}")
					else:
						download_genome(ftp_path, compressed_file, extracted_file)
				else:
					print(f"No reference genome found for {species_name}.")
					species_name = 'NotFound'
					return('NotFound', 'NoFile')
				return(species_name.replace(' ', '_'), extracted_file, qfas)
			
			adapt_changes()
			print(self.input_dic)

			tag = docker_tag('fastani')
			fastani_container = 'quay.io/biocontainers/fastani:' + tag
			client = docker.from_env()
			
			for key in self.input_dic: # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
				if self.manual_ref == 'NA':
					ref_species, self.dir_path['ref_file'], qfas = species_search(
									f"{self.input_dic[key][2]}/{self.input_dic[key][3]}", user_home('refseqdir'))
					os.remove(f"{user_home('anioutdir')}/{qfas}")
					os.remove(f"{user_home('anioutdir')}/{qfas}.xml")
				else:
					ref_species = os.path.splitext(os.path.basename(self.dir_path['ref_file']))[0].replace(' ', '_')
				dt_now = datetime.datetime.now()
				if ref_species == 'NotFound':
					outfile = f"{self.dir_path['outdir']}/{key}-NotIdentified_{str(dt_now.strftime('%Y%m%d%H%M'))}.txt"
					with open(outfile, 'w') as f:
						f.write('')
				else:
					ref_dir = os.path.dirname(self.dir_path['ref_file'])
					ref_file = os.path.basename(self.dir_path['ref_file'])
					outfile = f"{key}-{ref_species}_{str(dt_now.strftime('%Y%m%d%H%M'))}.txt"
					ani_cmd = f"fastANI -q /mnt/{self.input_dic[key][3]} -r /media/{ref_file} -o {outfile}"
					print(self.input_dic[key])
					client.containers.run(fastani_container, ani_cmd, remove=True, 
						volumes=[f"{self.input_dic[key][2]}:/mnt", f"{ref_dir}:/media", f"{self.dir_path['outdir']}:/home"], 
						working_dir='/home')
					client.containers.run(fastani_container, f"chmod 777 {outfile}", remove=True, 
						volumes=[f"{self.dir_path['outdir']}:/home"], working_dir='/home')
			
			self.dir_path['ref_file'] = ''
			ReviewWindow.destroy()
			
		if len(self.fasta_dic) >= 1:
			for key in self.fasta_dic:
				self.input_dic[key] = ['fasta', key, self.fasta_dic[key][0], self.fasta_dic[key][1], self.fasta_dic[key][2]]
		print(self.input_dic)
		print(self.use_db)
			
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
		for key in self.input_dic: # input_dic[strain] = {file_type, strain, dir, seq1, seq2}
			tree.insert(parent='', index='end', iid=i ,values=(self.input_dic[key][0], self.input_dic[key][1], 
				self.input_dic[key][2], self.input_dic[key][3]))
			i += 1

		tree.pack(pady=50)
		buttonCancel = tk.Button(ReviewWindow, text = "Return to file selection", command=close_Window, width=18, height=3)
		buttonCancel.place(x=600, y=320)
		buttonRun = tk.Button(ReviewWindow, text = "Run fastANI", command=run_ani, width=18, height=3)
		buttonRun.place(x=300, y=320)
		label_msg1 = tk.Label(ReviewWindow, text='Double-click to delete record. To add data, return to the previous screen.', font=font.Font(size=16))
		label_msg1.place(x=50, y=280)
		
	
def main():
	root = tk.Tk()
	app = createANIWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

