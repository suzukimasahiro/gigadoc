#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#             Shared function                                                   #
#                                                                               #
#################################################################################

# 2024/02/05
# 2023/07/05 
# 2023/01/05

import os
import os.path
import re
import json
import webbrowser
from urllib.error import HTTPError
from Bio import Entrez, SeqIO

def system_home():
	if os.name == 'nt':
		win_dir = os.path.expanduser('~').split('\\')
		system_home_dir = win_dir[0] + '/' + win_dir[1] + '/' + win_dir[2]
	else:
		system_home_dir = os.path.expanduser('~')
	return(system_home_dir)

def user_home(dir_name):
	settings_dic = settings()
	return(settings_dic[dir_name])

def illumina_fastq(file_name):
	file_part = os.path.basename(file_name).split('_')
		### strain_R1_fastp.fastq.gz (after fastp trimming)
	sample = file_part[0]
	if '_R1_' in file_part:
		R1 = os.path.basename(file_name)
		R2 = R1.replace('_R1_', '_R2_')
	else:
		R2 = os.path.basename(file_name)
		R1 = R2.replace('_R2_', '_R1_')
	return([sample, os.path.dirname(file_name), R1, R2])

def jump_to_link(url):
	webbrowser.open_new(url)


def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return True
    else:
        return False

def dl_gbseq(acc_no, ret_type, outfile, mode, e_mail):
	Entrez.email = e_mail
	attempt = 0
	while attempt < 3:
		attempt += 1
		try:
			net_handle = Entrez.efetch(db='nucleotide', id=acc_no, rettype=ret_type, retmode='text')
		except HTTPError as err:
			if 500 <= err.code <= 599:
				print("Received error from server %s" % err)
				print("Attempt %i of 3" % attempt)
				time.sleep(15)
			else:
				raise
		else:
			break
	out_handle = open(outfile, mode)
	out_handle.write(net_handle.read())
	out_handle.close()
	net_handle.close()

def chk_dir(parent_dir, new_dir):
	if os.path.isdir(parent_dir + new_dir):
		pass
	else:
		os.mkdir(parent_dir + new_dir)

def settings():
	syshome = system_home()
	settings_dic = {}
	try:
		if os.path.isfile(syshome + '/gigadoc/settings/gigadoc_settings.yaml'):
			with open(syshome + '/gigadoc/settings/gigadoc_settings.yaml', 'r')as f:
				settings_dic = json.load(f)
	except:
		pass
	##### default settings #####
	chk_dir(syshome, '/gigadoc')
	gigadocdir = syshome + '/gigadoc'
	chk_dir(gigadocdir, '/settings')
	chk_dir(gigadocdir, '/out')
	chk_dir(gigadocdir + '/out', '/assembly')
	chk_dir(gigadocdir + '/out', '/amrfinder')
	chk_dir(gigadocdir + '/out', '/mlst')
	chk_dir(gigadocdir + '/out', '/snippy')
	chk_dir(gigadocdir + '/out', '/ANI')
	chk_dir(gigadocdir, '/cgMLST')
	chk_dir(gigadocdir, '/database')
	chk_dir(gigadocdir + '/database', '/amrfinderdb')
	chk_dir(gigadocdir + '/database', '/ref_genome')
	chk_dir(gigadocdir + '/database', '/blastdb')
		
	outdir = syshome + '/gigadoc/out'
	cgMLSTdir = syshome + '/gigadoc/cgMLST'
	dbdir = syshome + '/gigadoc/database'
	assemblydir = outdir + '/assembly'
	mlstoutdir = outdir + '/mlst'
	amrfinderdir = outdir + '/amrfinder'
	snippydir = outdir + '/snippy'
	anioutdir = outdir + '/ANI'
	amrfinderdbdir = dbdir + '/amrfinderdb'
	refseqdir = dbdir + '/ref_genome'
	blastdbdir = dbdir + '/blastdb'
		
	if 'email' not in settings_dic:
		settings_dic['email'] = ''
	if 'gigadocdir' not in settings_dic:
		settings_dic['gigadocdir'] = gigadocdir
	if 'datadir' not in settings_dic:
		settings_dic['datadir'] = syshome
	if 'outdir' not in settings_dic:
		settings_dic['outdir'] = outdir
	if 'cgMLSTdir' not in settings_dic:
		settings_dic['cgMLSTdir'] = cgMLSTdir
	if 'assemblydir' not in settings_dic:
		settings_dic['assemblydir'] = assemblydir
	if 'mlstoutdir' not in settings_dic:
		settings_dic['mlstoutdir'] = mlstoutdir
	if 'amrfinderdir' not in settings_dic:
		settings_dic['amrfinderdir'] = amrfinderdir
	if 'snippydir' not in settings_dic:
		settings_dic['snippydir'] = snippydir
	if 'anioutdir' not in settings_dic:
		settings_dic['anioutdir'] = anioutdir
	if 'dbdir' not in settings_dic:
		settings_dic['dbdir'] = dbdir
	if 'amrfinderdbdir' not in settings_dic:
		settings_dic['amrfinderdbdir'] = amrfinderdbdir
	if 'refseqdir' not in settings_dic:
		settings_dic['refseqdir'] = refseqdir
	if 'blastdbdir' not in settings_dic:
		settings_dic['blastdbdir'] = blastdbdir
	return(settings_dic)

def update_settings(data_dir, out_dir, cgMLST_dir, db_dir, email):
	settings_dic = settings()
	settings_dic['email'] = email
	settings_dic['datadir'] = data_dir
	settings_dic['outdir'] = out_dir
	settings_dic['cgMLSTdir'] = cgMLST_dir
	settings_dic['assemblydir'] = f"{out_dir}/assembly"
	settings_dic['mlstoutdir'] = f"{out_dir}/mlst"
	settings_dic['amrfinderdir'] = f"{out_dir}/amrfinder"
	settings_dic['snippydir'] = f"{out_dir}/snippy"
	settings_dic['anioutdir'] = f"{out_dir}/ANI"
	settings_dic['dbdir'] = db_dir
	settings_dic['amrfinderdbdir'] = f"{db_dir}/amrfinderdb"
	settings_dic['refseqdir'] = f"{db_dir}/ref_genome"
	settings_dic['blastdbdir'] = f"{db_dir}/blastdb"
	
	chk_dir(out_dir, '/assembly')
	chk_dir(out_dir, '/amrfinder')
	chk_dir(out_dir, '/mlst')
	chk_dir(out_dir, '/snippy')
	chk_dir(out_dir, '/ANI')
	chk_dir(db_dir, '/amrfinderdb')
	chk_dir(db_dir, '/ref_genome')
	chk_dir(db_dir, '/blastdb')

	with open(system_home() + '/gigadoc/settings/gigadoc_settings.yaml', 'w')as f:
		json.dump(settings_dic, f, indent=2)
	


def spades_contig(file_path):
	fasta_files = []
	fasta_dic = {}
	try:
		fasta_files = fasta_files + glob.glob(file_path + '/*/SPAdes/*_contigs.fasta')
		fasta_files = fasta_files + glob.glob(file_path + '/SPAdes/*_contigs.fasta')
		fasta_files = fasta_files + glob.glob(file_path + '/*_contigs.fasta')
	except:
		return('NotFound')
	if len(fasta_files) > 0:
		for fasta in fasta_files:
			strain = os.path.splitext(os.path.basename(fasta))[0].replace('_contigs', '')
			dir_name = os.path.dirname(fasta)
			if os.name == 'nt':
				dir_name = dir_name.replace(os.sep,'/')
			filename = os.path.basename(fasta)
			fasta_dic[strain] = [dir_name, filename, '']
	else:
		return('NotFound')

def select_fastq(file_path):
	fastq_files =[]
	fastq_dic = {}
	try:
		fastq_files = fastq_files + glob.glob(file_path + '/*/fastp/*_R1_*.fq.gz')
		fastq_files = fastq_files + glob.glob(file_path + '/fastp/*_R1_*.fq.gz')
		fastq_files = fastq_files + glob.glob(file_path + '/*_R1_*.fq.gz')
		fastq_files = fastq_files + glob.glob(file_path + '/*/fastp/*_R1_*.fastq.gz')
		fastq_files = fastq_files + glob.glob(file_path + '/fastp/*_R1_*.fastq.gz')
		fastq_files = fastq_files + glob.glob(file_path + '/*_R1_*.fastq.gz')
	except:
		return('NotFound')
	if len(fastq_files) > 0:
		for fastq in fastq_files:
			seq_list = illumina_fastq(fastq)
			if seq_list[0] == 'Undetermined':
				pass
			else:
				fastq_dic[seq_list[0]] = [seq_list[1], seq_list[2], seq_list[3]]
					# seq_list[0]:strain, seq_list[1]:dir_name, seq_list[2]:Read1, seq_list[3]:Read2
		return(fastq_dic)
	else:
		return('NotFound')
