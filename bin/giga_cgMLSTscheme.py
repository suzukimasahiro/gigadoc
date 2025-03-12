#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#         GIGAdoc cgMLSTscheme, prepareing database for cgMLST                  #
#                                                                               #
#################################################################################

# 2025/03/12 Support cgMLST.org (Ridom) scheme
# 2023/12/06 Ver.0.2

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import tkinter.font as font
import os
import os.path
import docker
import datetime
import psutil
import json
import requests
import urllib.request
import time
import zipfile
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, jump_to_link, is_valid_email, get_download_directory, dl_refGenomeSeq
from giga_cgMLSTsettings import cgmlst_schemes, prepare_dir, cgmlst_files, pubmlst_species


class createCgMLSTschemeWindow(tk.Frame):
	scheme = ''
	species = ''
	email = ''
	Ridom_zip = ''
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("Make cgMLST database")
		self.create_widgets()

	def create_widgets(self):
		########## Create tabs ##########
		tab_control = ttk.Notebook(self.master)
		
		tab_pubMLST = ttk.Frame(tab_control)
		tab_control.add(tab_pubMLST, text='pubMLST')
		tab_control.pack(expand=1, fill="both")

		tab_Ridom = ttk.Frame(tab_control)
		tab_control.add(tab_Ridom, text='cgMLST.org (Ridom)')
		tab_control.pack(expand=1, fill="both")

		### Create frame
		frame = tk.Frame(self.master, width=800, height=90, relief=tk.GROOVE, bd=2)
		frame.propagate(False)
		frame.pack()

		########## input E-mail ##########
		label_email = tk.Label(self.master, text='E-mail:', font=font.Font(size=12))
		label_email.place(x=20, y=123)
		Email_box = tk.Entry(self.master, width=38)
		Email_box.insert(0, user_home('email'))
		Email_box.place(x=90, y=123)

		########## pubMLST ##########
		def select_combo(event):
			self.scheme = comboSelectScheme.get()
			buttonMakeDB = tk.Button(tab_pubMLST,
									text='Download and\nmake DB',
									command=push_makedb, 
									width=14,
									height=3,
									state='normal'
									)
			buttonMakeDB.place(x=530, y=5)
			idir = user_home('cgMLSTdir')
			label_outdir = tk.Label(tab_pubMLST, text=f'Database will be placed on', font=font.Font(size=12))
			label_outdir.place(x=20, y=50)
			label_dldir = tk.Label(tab_pubMLST,
							text=f"{idir}{cgmlst_files(self.scheme, 'dbdir')} \
							                                                                        ",
							font=font.Font(size=12))
			label_dldir.place(x=20, y=70)

		def push_makedb():
			self.email = Email_box.get()
			if is_valid_email(self.email):
				self.make_pubMLST_DB()
			else:
				messagebox.showerror('ERROR', 'Enter E-mail address')

		mem = psutil.virtual_memory()
		if mem.total >= 8000000000: # cgMLST requires 8 Gbytes or more memory
			value = tk.StringVar()
			comboSelectScheme = ttk.Combobox(tab_pubMLST,
								state="readonly",
								values = cgmlst_schemes('key'),
								textvariable = value,
								width = 45
								)
			comboSelectScheme.bind('<<ComboboxSelected>>', select_combo)
		else:
			comboSelectScheme = ttk.Combobox(tab_pubMLST, state="disable", width = 45)
		comboSelectScheme.place(x=20, y=15)
		
		buttonDummyMakeDB = tk.Button(tab_pubMLST, text='Download and\nmake DB', 
			command=push_makedb, width=14, height=3, state='disable')
		buttonDummyMakeDB.place(x=530, y=5)

		label_pubMLST = tk.Label(tab_pubMLST, text= 'Link to pubMLST: https://pubmlst.org/', 
			font=font.Font(size=12), fg='#0000ff')
		label_pubMLST.place(x=20, y=130)
		label_pubMLST.bind('<Button-1>', lambda e:jump_to_link('https://pubmlst.org/'))
		
		label_BIGSdb = tk.Label(tab_pubMLST,
			text= 'Link to BIGSdb API: https://bigsdb.readthedocs.io/en/latest/rest.html#db-db', 
			font=font.Font(size=12), fg='#0000ff')
		label_BIGSdb.place(x=20, y=155)
		label_BIGSdb.bind('<Button-1>', lambda e:jump_to_link('https://bigsdb.readthedocs.io/en/latest/rest.html#db-db'))

		########## Ridom ##########
		def open_Ridom():
			jump_to_link('https://www.cgmlst.org/ncs')
			
		def select_RidomScheme():
			fTyp = [('cgMLST_alleles.zip', '*cgMLST_alleles.zip')]
			self.Ridom_zip = filedialog.askopenfilename(parent = self.master,filetypes=fTyp, 
														initialdir=get_download_directory()
														) # 2025/02/25
			buttonRidomBuild = tk.Button(tab_Ridom, text = "Build cgMLST scheme", 
										command=push_makeRidomDB, width=18, height=3
										)
			buttonRidomBuild.place(x=480, y=20)
			print(self.Ridom_zip)

		def push_makeRidomDB():
			self.email = Email_box.get()
			if is_valid_email(self.email):
				self.make_Ridom_DB()
			else:
				messagebox.showerror('ERROR', 'Enter E-mail address')
	

		buttonRidom = tk.Button(tab_Ridom, text = "Open cgMLST.org\nNomenclature Server", 
			command=open_Ridom, width=18, height=3)
		buttonRidom.place(x=20, y=20)

		buttonRidomScheme = tk.Button(tab_Ridom, text = "Select zipped\nscheme file", 
			command=select_RidomScheme, width=18, height=3)
		buttonRidomScheme.place(x=250, y=20)

		buttonDummyBuild = tk.Button(tab_Ridom, text = "Build cgMLST scheme", 
			command=self.make_Ridom_DB, width=18, height=3, state='disable')
		buttonDummyBuild.place(x=480, y=20)

		label_Ridom = tk.Label(tab_Ridom, text= 'Link to cgMLST.org Nomenclature Server: https://www.cgmlst.org/ncs', 
			font=font.Font(size=12), fg='#0000ff')
		label_Ridom.place(x=20, y=155)
		label_Ridom.bind('<Button-1>', lambda e:jump_to_link('https://www.cgmlst.org/ncs'))

		########## Frame ##########
		buttonCancel = tk.Button(frame, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=630, y=10)

		label_chewBBACA = tk.Label(frame, text= 'Link to chewBBACA: https://github.com/B-UMMI/chewBBACA', 
			font=font.Font(size=12), fg='#0000ff')
		label_chewBBACA.place(x=20, y=10)
		label_chewBBACA.bind('<Button-1>', lambda e:jump_to_link('https://github.com/B-UMMI/chewBBACA'))

		label_prodigal = tk.Label(frame, text= 'Link to Prodigal: https://github.com/hyattpd/Prodigal', 
			font=font.Font(size=12), fg='#0000ff')
		label_prodigal.place(x=20, y=35)
		label_prodigal.bind('<Button-1>', lambda e:jump_to_link('https://github.com/hyattpd/Prodigal'))
		

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		widgets = [label_pubMLST, label_BIGSdb, label_chewBBACA, label_prodigal, label_Ridom]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))

	def close_Window(self):
		self.master.destroy()
		
		
	def make_pubMLST_DB(self):
		def get_loci(url_cgMLST):
			loci_list = []
			cgMLST_loci = requests.get(url_cgMLST)
			description = cgMLST_loci.json()['description']
			for value in cgMLST_loci.json()['loci']:
				loci_list.append(value)
			return(description.replace(' ', '_'), loci_list)
		
		def dl_alleles(locus_no):
			locus = loci_list[locus_no]
			locus_file = dl_dir + '/' + os.path.basename(locus) + '.fasta'
			fasta = locus + '/alleles_fasta'
			i = 0
			while i < 2:
				i += 1
				if os.path.isfile(locus_file):
					print(fasta, 'ok')
					break
				else:
					print(fasta)
					attempt = 0
					while attempt < 3:
						attempt += 1
						try:
							seq = urllib.request.urlopen(fasta, timeout=10).read()
							with open(locus_file, 'bw') as f:
								f.write(seq)
						except:
							time.sleep(15)
						else:
							break
		#dl_dir, tre_dir = dir_check()	
		prepare_dir(self.scheme)
		self.species = pubmlst_species(self.scheme)
		description, loci_list = get_loci(cgmlst_schemes(self.scheme))
		dl_dir = cgmlst_files(self.scheme, 'cgMLSTdir') + cgmlst_files(self.scheme, 'allelesdir')
		for i in range(len(loci_list)):
			dl_alleles(i)

		self.prepare_training()
		self.build_DB()

	def make_Ridom_DB(self):
		def unzip_file(zip_path, extract_to=None):
			"""
			Unzips a ZIP file containing multiple files.
			:param zip_path: Path to the ZIP file
			:param extract_to: Destination folder (optional). Defaults to the same directory as the ZIP file.
			"""
			if extract_to is None:
				extract_to = os.path.dirname(zip_path)
			
			# Ensure the extraction directory exists
			os.makedirs(extract_to, exist_ok=True)
			
			with zipfile.ZipFile(zip_path, 'r') as zip_ref:
				zip_ref.extractall(extract_to)
				print(f"Extracted all files to: {extract_to}")
		
		def extract_scheme(scheme_zip):
			compressed_file = os.path.basename(scheme_zip)
			return(f"{compressed_file.replace('_cgMLST_alleles.zip', '')}_Ridom")

		print('make_Ridom_DB')
		self.scheme = extract_scheme(self.Ridom_zip)
		genus = self.scheme.split('_')[0]
		sp = self.scheme.split('_')[1]
		self.species = f"{genus} {sp}"
		print(self.species, self.scheme)
		dl_dir = cgmlst_files(self.scheme, 'cgMLSTdir') + cgmlst_files(self.scheme, 'allelesdir')
		unzip_file(self.Ridom_zip, dl_dir)

		self.prepare_training()
		self.build_DB()

		
	def prepare_training(self):
		def make_training(scheme):
			cgmlst_dir = cgmlst_files(scheme, 'cgMLSTdir')
			trn_dir = cgmlst_files(scheme, 'trndir')
			ref_file = cgmlst_files(scheme, 'ref')
			trn_file = cgmlst_files(scheme, 'trn')
			if os.path.isfile(cgmlst_dir + trn_dir + '/' + ref_file):
				return()
			else:
				dl_refGenomeSeq(self.species, self.email)
				#dl_refgenome(cgmlst_dir + trn_dir + '/' + ref_file, scheme)
				prodigal(ref_file, trn_file, cgmlst_dir + trn_dir)
		'''
		def dl_refgenome(ref_file, scheme):
			for acc_no in cgmlst_reference(scheme)[1]:
				print(acc_no)
				dl_gbseq(acc_no, 'fasta', ref_file, 'a', self.email)
		'''
		
		def prodigal(input_file, trn_file, trn_dir):
			tag = docker_tag('prodigal')
			prodigal_container = 'quay.io/biocontainers/prodigal:' + tag
			client = docker.from_env()
			prodigal_cmd = f"prodigal -i /media/{input_file} -t {trn_file}"
			client.containers.run(prodigal_container, prodigal_cmd, remove=True, platform = 'linux/x86_64', 
					volumes=[f"{trn_dir}:/mnt", f"{user_home('refseqdir')}:/media"], working_dir='/mnt')
			chmod_cmd = f"chmod 777 {trn_file}"
			client.containers.run(prodigal_container, chmod_cmd, remove=True, platform = 'linux/x86_64', 
					volumes=[trn_dir + ':/mnt'], working_dir='/mnt')
		make_training(self.scheme)

	def build_DB(self):
		def externalSchema(scheme):
			cgmlst_dir = cgmlst_files(scheme, 'cgMLSTdir')
			trn_dir = cgmlst_files(scheme, 'trndir')
			trn_file = cgmlst_files(scheme, 'trn')
			alleles_dir = cgmlst_files(scheme, 'allelesdir')
			schemes_dir = cgmlst_files(scheme, 'schemesdir')
			db_dir = cgmlst_files(scheme, 'dbdir')
			scheme_name = cgmlst_files(scheme, 'each_scheme')
			tag = docker_tag('chewbbaca')
			chewbbaca_container = 'quay.io/biocontainers/chewbbaca:' + tag
			client = docker.from_env()
			chewbbaca_cmd = 'chewBBACA.py PrepExternalSchema -g /mnt' + alleles_dir + \
			' -o /mnt' + db_dir + ' --ptf /mnt' + trn_dir + '/' + trn_file
			client.containers.run(chewbbaca_container, chewbbaca_cmd, remove=True, platform = 'linux/x86_64', 
					volumes=[cgmlst_dir + ':/mnt'], working_dir='/mnt')

			##### change permissions #####
		def chmod_scheme(scheme):
			cgmlst_dir = cgmlst_files(scheme, 'cgMLSTdir')
			schemes_dir = cgmlst_files(scheme, 'schemesdir')
			scheme_name = cgmlst_files(scheme, 'each_scheme')
			client = docker.from_env()
			container = client.containers.run('ubuntu', detach=True, tty=True,
					volumes=[cgmlst_dir + schemes_dir + ':/mnt'], working_dir='/mnt')
			#chmod_cmd = "ls"
			chmod_cmd = "/bin/bash -c \"chmod 777 {}\"".format(scheme_name)
			exec_response = container.exec_run(chmod_cmd)

			chmod_cmd =  "/bin/bash -c \"chmod 777 {}/*\"".format(scheme_name)
			exec_response = container.exec_run(chmod_cmd)

			container.stop()
			container.remove()
			

		#dl_dir, tre_dir = dir_check()	
		#make_training(self.scheme)
		print('Making scheme. This takes time.')
		externalSchema(self.scheme)
		print('Done!')
		chmod_scheme(self.scheme)
		
		'''
		docker run --rm -v ~/temp:/mnt -v ~/work:/media quay.io/biocontainers/chewbbaca:3.2.0--pyhdfd78af_0 \
			chewBBACA.py PrepExternalSchema -i /mnt/Enterobase_Ecoli_cgmlst -o /mnt/chewout2 \
			--ptf /mnt/prodigal_training_files/Escherichia_coli.trn
		'''
		
	
def main():
	root = tk.Tk()
	app = createCgMLSTschemeWindow(master=root)
	app.mainloop()

if __name__ == "__main__":
	main()

