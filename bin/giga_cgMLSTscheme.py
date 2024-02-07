#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#         GIGAdoc cgMLSTscheme, prepareing database for cgMLST                  #
#                                                                               #
#################################################################################

# 2023/12/06 Ver.0.2

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
from gigadoc_tags import docker_tag
from gigadoc_functions import user_home, jump_to_link, is_valid_email, dl_gbseq
from cgMLST_settings import cgmlst_schemes, cgmlst_reference, prepare_dir, cgmlst_files


class createCgMLSTschemeWindow(tk.Frame):
	scheme = ''
	email = ''
	def __init__(self, master  = None):
		super().__init__(master)
		
		self.master.geometry("800x300+50+250")
		self.master.title("Make cgMLST database")
		self.create_widgets()

	def create_widgets(self):
		def select_combo(event):
			self.scheme = comboSelectScheme.get()
			buttonMakeDB = tk.Button(self.master,
			text='Download and\nmake DB',
			command=push_makedb, 
			width=14,
			height=3,
			state='normal'
			)
			buttonMakeDB.place(x=530, y=15)
			idir = user_home('cgMLSTdir')
			label_outdir = tk.Label(self.master, text=f'Database will be placed on', font=font.Font(size=12))
			label_outdir.place(x=20, y=90)
			label_dldir = tk.Label(self.master,
							text=f"{idir}{cgmlst_files(self.scheme, 'dbdir')} \
							                                                                        ",
							font=font.Font(size=12))
			label_dldir.place(x=20, y=110)

		def push_makedb():
			self.email = Email_box.get()
			if is_valid_email(self.email):
				self.makeDB()
			else:
				messagebox.showerror('ERROR', 'Enter E-mail address')

		mem = psutil.virtual_memory()
		if mem.total >= 8000000000: # cgMLST requires 8 Gbytes or more memory
			value = tk.StringVar()
			comboSelectScheme = ttk.Combobox(self.master,
								state="readonly",
								values = cgmlst_schemes('key'),
								textvariable = value,
								width = 45
								)
			comboSelectScheme.bind('<<ComboboxSelected>>', select_combo)
		else:
			comboSelectScheme = ttk.Combobox(self.master, state="disable", width = 45)
		comboSelectScheme.place(x=20, y=25)
		
		label_email = tk.Label(self.master, text='E-mail:', font=font.Font(size=12))
		label_email.place(x=20, y=60)
		Email_box = tk.Entry(self.master, width=38)
		Email_box.insert(0, user_home('email'))
		Email_box.place(x=90, y=60)

		buttonDummyMakeDB = tk.Button(self.master, text='Download and\nmake DB', 
			command=push_makedb, width=14, height=3, state='disable')
		buttonDummyMakeDB.place(x=530, y=15)

		buttonCancel = tk.Button(self.master, text = "Close", 
			command=self.close_Window, width=14, height=3)
		buttonCancel.place(x=630, y=200)

		def change_cursor(widget, cursor):
			widget.config(cursor=cursor)

		label_pubMLST = tk.Label(self.master, text= 'Link to pubMLST: https://pubmlst.org/', 
			font=font.Font(size=12), fg='#0000ff')
		label_pubMLST.place(x=20, y=180)
		label_pubMLST.bind('<Button-1>', lambda e:jump_to_link('https://pubmlst.org/'))
		
		label_BIGSdb = tk.Label(self.master,
			text= 'Link to BIGSdb API: https://bigsdb.readthedocs.io/en/latest/rest.html#db-db', 
			font=font.Font(size=12), fg='#0000ff')
		label_BIGSdb.place(x=20, y=205)
		label_BIGSdb.bind('<Button-1>', lambda e:jump_to_link('https://bigsdb.readthedocs.io/en/latest/rest.html#db-db'))

		label_chewBBACA = tk.Label(self.master, text= 'Link to chewBBACA: https://github.com/B-UMMI/chewBBACA', 
			font=font.Font(size=12), fg='#0000ff')
		label_chewBBACA.place(x=20, y=230)
		label_chewBBACA.bind('<Button-1>', lambda e:jump_to_link('https://github.com/B-UMMI/chewBBACA'))

		label_prodigal = tk.Label(self.master, text= 'Link to Prodigal: https://github.com/hyattpd/Prodigal', 
			font=font.Font(size=12), fg='#0000ff')
		label_prodigal.place(x=20, y=255)
		label_prodigal.bind('<Button-1>', lambda e:jump_to_link('https://github.com/hyattpd/Prodigal'))

		widgets = [label_pubMLST, label_BIGSdb, label_chewBBACA, label_prodigal]
		for widget in widgets:
			widget.bind("<Enter>", lambda event, w=widget: change_cursor(w, "hand2"))
			widget.bind("<Leave>", lambda event, w=widget: change_cursor(w, ""))

	def close_Window(self):
		self.master.destroy()
		
	def makeDB(self):
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

		def make_training(scheme):
			cgmlst_dir = cgmlst_files(scheme, 'cgMLSTdir')
			trn_dir = cgmlst_files(scheme, 'trndir')
			ref_file = cgmlst_files(scheme, 'ref')
			trn_file = cgmlst_files(scheme, 'trn')
			if os.path.isfile(cgmlst_dir + trn_dir + '/' + ref_file):
				return()
			else:
				dl_refgenome(cgmlst_dir + trn_dir + '/' + ref_file, scheme)
				prodigal(ref_file, trn_file, cgmlst_dir + trn_dir)
			
		def dl_refgenome(ref_file, scheme):
			for acc_no in cgmlst_reference(scheme)[1]:
				print(acc_no)
				dl_gbseq(acc_no, 'fasta', ref_file, 'a', self.email)
		
		def prodigal(input_file, trn_file, trn_dir):
			tag = docker_tag('prodigal')
			prodigal_container = 'quay.io/biocontainers/prodigal:' + tag
			client = docker.from_env()
			prodigal_cmd = 'prodigal -i ' + input_file + ' -t ' + trn_file
			client.containers.run(prodigal_container, prodigal_cmd, remove=True, 
					volumes=[trn_dir + ':/mnt'], working_dir='/mnt')
			chmod_cmd = 'chmod 777 ' + trn_file
			client.containers.run(prodigal_container, chmod_cmd, remove=True, 
					volumes=[trn_dir + ':/mnt'], working_dir='/mnt')

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
			chewbbaca_cmd = 'chewBBACA.py PrepExternalSchema -i /mnt' + alleles_dir + \
			' -o /mnt' + db_dir + ' --ptf /mnt' + trn_dir + '/' + trn_file
			client.containers.run(chewbbaca_container, chewbbaca_cmd, remove=True, 
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
		prepare_dir(self.scheme)
		make_training(self.scheme)
		description, loci_list = get_loci(cgmlst_schemes(self.scheme))
		dl_dir = cgmlst_files(self.scheme, 'cgMLSTdir') + cgmlst_files(self.scheme, 'allelesdir')
		for i in range(len(loci_list)):
			dl_alleles(i)
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

