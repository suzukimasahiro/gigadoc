#!/usr/bin/python3
# -*- coding:utf-8 -*-

# 2025/02/26 Support organism and plus options
# 2024/01/05 Count copy number on summary tab in EXCEL report
# 2023/06/12 Fix results order to that of the input list
# 2023/04/27 Change threshold of "partial" to <100 for Excel report
# 2022/12/26 update to use with GIGA_amrfinder
# 2022/05/19 update
# 2022/04/08 update
# 2022/02/09


import argparse
import pandas as pd
import numpy as np
import subprocess
import sys
from subprocess import PIPE
from multiprocessing import Pool, Manager

def amrfinder(strain): # "amrfinder" is running in "run_amrfinder'
	results_list = []
	strain_name = file_list[strain][0]
	fasta = file_list[strain][1]
	identity = file_list[strain][2]
	organism = file_list[strain][3]
	plus = file_list[strain][4]

	amrfinder_command = ['amrfinder', '-n', fasta, '-i', identity]
	if organism in organism():
		amrfinder_command.append('-O')
		amrfinder_command.append(organism)
	if plus == '--plus':
		amrfinder_command.append('--plus')
		
	res = subprocess.run(amrfinder_command, stdout=PIPE)
	amr_list = res.stdout.decode('utf8').rstrip().split("\n")
	for amr_line in amr_list:
		if 'Alignment' in amr_line:
			pass
		else:
			results_list.append(amr_summary(amr_line, organism))
	results_dic[file_list[strain_name]] = results_list
	results_text_dic[file_list[strain_name]] = res.stdout.decode('utf8')

def amrfinder_version():
	amrfinder_command = ['amrfinder', '-V']
	res = subprocess.run(amrfinder_command, stdout=PIPE)
	ver_list = res.stdout.decode('utf8').rstrip().split("\n")
	version_dic = {}
	for ver_info in ver_list:
		if 'Software version' in ver_info:
			version_dic['Software version'] = ver_info.split(' ')[2]
		elif 'Database version' in ver_info:
			version_dic['Database version'] = ver_info.split(' ')[2]
	return(version_dic)
		
	
def amr_summary(line, organism): # 2022/4/8
	elements = line.split('\t')
	contig_id = elements[1]
	gene_symbol = elements[5]
	protein_name = elements[6]
	closest_protein = elements[19]
	amr_class = elements[10]
	subclass = elements[11]
	coverage = float(elements[15])
	identity = float(elements[16])
	gene_info = protein_name + ' ' + closest_protein
	word_list = gene_info.split(' ')
	bla_identifier = ''
	qry_word = gene_symbol
	gene_identifier = gene_symbol.split('_')[0]
	if len(gene_symbol) > 3:
		if gene_symbol[0:3] == 'bla':
			bla_identifier = 'bla'
			qry_word = gene_symbol[3:]
	identifier = gene_symbol
	num_word = len(word_list)
	for i in range(num_word):
		if qry_word.lower() in word_list[i].lower():
			if i+1 < num_word and word_list[i+1] == 'family':
				continue
			identifier = word_list[i]
	if gene_symbol.lower() == identifier.lower():
		identifier = gene_symbol
	if bla_identifier == 'bla' and len(identifier) >= 3 and identifier[0:3].lower() != 'bla':
		identifier = bla_identifier + identifier
	if point_mutation(organism, gene_identifier):
		pass
	else:
		if coverage < 100:
			identifier = identifier + '_partial'
		elif identity < 100:
			identifier = identifier + '_closest'
	return([identifier, protein_name, closest_protein, amr_class, subclass, coverage, identity, contig_id])

def amr_resultsfile(resultsfile):
	with open(resultsfile, 'r') as f:
		results_lines = f.read().rstrip().split('\n')
	resultsfile_dic = {}
	strain_temp = []
	for line in results_lines:
		if '\t' not in line and line != '' :
			strain_id = line.rstrip()
			resultsfile_dic[strain_id] = []
			strain_temp.append(strain_id)
		elif 'Protein identifier' in line or line == '':
			continue
		else:
			resultsfile_dic[strain_id].append(amr_summary(line))
	return(resultsfile_dic, strain_temp)

def amr2excel(results_dic, out_name, strain_list, verInfo_dic, seq_ident, transpose): #2023/6/9
	gene_list = []
	gene_info_list = []
	for key in results_dic: #2022/4/8
		for each_element in results_dic[key]:
			identifier = each_element[0]
			protein_name = each_element[1]
			amr_class = each_element[3]
			subclass = each_element[4]
			closest_protein = each_element[2]
			if identifier not in gene_list:
				gene_list.append(identifier)			
				gene_info_list.append([identifier, protein_name, amr_class, subclass, closest_protein])
	temp_df = pd.DataFrame(gene_info_list, columns = 
		['Gene symbol' , 'Protein name' , 'Class' , 'Subclass', 'Closest protein'])
	# 2025/02/26 Sort by "Class" and "Gene symbol"
	df_gene_info = temp_df.loc[
			temp_df.sort_values(
			by=['Class', 'Gene symbol'],
			key=lambda x: [
				(float('inf'), gene_symbol) if class_name == 'NA' else (ord(class_name[0]), gene_symbol)
				for class_name, gene_symbol in zip(temp_df['Class'], temp_df['Gene symbol'])
			],
			ascending=[True, True]
		).index
	].reset_index(drop=True)
	gene_list = df_gene_info['Gene symbol'].tolist()
	num_strain = len(results_dic)
	num_gene = len(gene_list)
	
	verInfo_dic['MIN_IDENT'] = float(seq_ident)
	verInfo_dic['MIN_COV'] = 0.5

	df_gene_table = pd.DataFrame(np.zeros((num_strain, num_gene), dtype = int), 
		columns = gene_list, index = strain_list)
	df_cov_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list)
	df_ident_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list)
	df_contig_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list).astype('object')
	df_version = pd.DataFrame([verInfo_dic], index=['Value'])
	print('run_mrfinder', verInfo_dic)

	for key in results_dic:
		for each in results_dic[key]:
			df_gene_table.at[key, each[0]] = df_gene_table.at[key, each[0]] + 1
			df_cov_table.at[key, each[0]] = float(each[5])
			df_ident_table.at[key, each[0]] = float(each[6])
			df_contig_table.at[key, each[0]] = each[7]

	print(df_gene_table)

	with pd.ExcelWriter(out_name + '_amrfinder.xlsx') as writer:
		if transpose:
			df_gene_table.T.to_excel(writer, sheet_name='summary')
			df_cov_table.T.to_excel(writer, sheet_name='coverage')
			df_ident_table.T.to_excel(writer, sheet_name='seq_identity')
			df_contig_table.T.to_excel(writer, sheet_name='contig_id')
		else:
			df_gene_table.to_excel(writer, sheet_name='summary')
			df_cov_table.to_excel(writer, sheet_name='coverage')
			df_ident_table.to_excel(writer, sheet_name='seq_identity')
			df_contig_table.to_excel(writer, sheet_name='contig_id')
		df_gene_info.to_excel(writer, sheet_name='gene_info')
		df_version.T.to_excel(writer, sheet_name='version_info')

def amr2txt(resultsfile, results_text_dic, strain_list, out_name):
	with open(out_name + '.txt', 'w', newline='\n') as f:
		if resultsfile != '':
			with open(resultsfile, 'r') as r: #2023/6/9
				results_lines = r.read().rstrip().split('\n')
				for line in results_lines:
					f.write(line + '\n')
				f.write('\n')
		for key in strain_list: #2023/6/9
			f.write(key + '\n')
			f.write(results_text_dic[key] + '\n')

def organisms():
	organis_list = (
					'Escherichia', 
					'Klebsiella_pneumoniae', 
					'Pseudomonas_aeruginosa', 
					'Acinetobacter_baumannii', 
					'Burkholderia_cepacia', 
					'Burkholderia_mallei', 
					'Burkholderia_pseudomallei', 
					'Campylobacter', 
					'Citrobacter_freundii', 
					'Clostridioides_difficile', 
					'Corynebacterium_diphtheriae', 
					'Enterobacter_asburiae', 
					'Enterobacter_cloacae', 
					'Enterococcus_faecalis', 
					'Enterococcus_faecium', 
					'Haemophilus_influenzae', 
					'Klebsiella_oxytoca', 
					'Neisseria_gonorrhoeae', 
					'Neisseria_meningitidis', 
					'Salmonella', 
					'Serratia_marcescens', 
					'Staphylococcus_aureus', 
					'Staphylococcus_pseudintermedius', 
					'Streptococcus_agalactiae', 
					'Streptococcus_pneumoniae', 
					'Streptococcus_pyogenes', 
					'Vibrio_cholerae', 
					'Vibrio_parahaemolyticus', 
					'Vibrio_vulnificus'
					)
	return(organis_list)

def point_mutation(organism, gene):
	gene_dic = {
				'Acinetobacter_baumannii': ['adeL', 'adeR', 'adeS', 'baeR', 'baeS', 'ftsI', 'gyrA', 'lpxA', 'lpxC',
								'parC', 'pmrA', 'pmrB', 'pmrC', 'rpoB'], 
				'Burkholderia_cepacia': ['ampD', 'amrR', 'gyrA'], 
				'Burkholderia_pseudomallei': ['amrR', 'bpeR', 'dut', 'gyrA', 'yciV'], 
				'Campylobacter': ['porA', 'rplV', 'rplD', 'rplV', 'cmeR', 'rplV', 'gyrA', 'rpsL'], 
				'Citrobacter_freundii': ['gyrA'], 
				'Clostridioides_difficile': ['dacS', 'gyrA', 'gyrB', 'mreE', 'murG', 'rpoB', 'rpoC', 'vanR-Cd', 'vanS-Cd'], 
				'Corynebacterium_diphtheriae': ['gyrA', 'rpoB'], 
				'Enterobacter_asburiae': ['baeS'], 
				'Enterobacter_cloacae': ['baeS', 'gyrA', 'parC'], 
				'Enterococcus_faecalis': ['cls', 'gshF', 'gyrA', 'liaF', 'liaR', 'liaS', 'parC', 'yybT'], 
				'Enterococcus_faecium': ['cls', 'dltC', 'eat(A)', 'gyrA', 'liaF', 'liaR', 'liaS', 'parC', 'pbp5', 'rpoB', 'rpoC'], 
				'Escherichia': ['acrB', 'acrR', 'baeS', 'basR', 'cirA', 'cyaA', 'emrR', 'fabG', 'fabI', 'folP', 'ftsI', 
								'gyrA', 'gyrB', 'lon', 'marR', 'murA', 'nfsA', 'nfsB', 'ompC', 'ompF', 'ompR', 'parC', 
								'parE', 'pmrB', 'ptsI', 'rpoB', 'rpsL', 'soxR', 'soxS', 'tufA', 'uhpA', 'uhpT'], 
				'Haemophilus_influenzae': ['folA', 'folP', 'ftsI', 'gyrA', 'parC', 'parE', 'rpoB'], 
				'Klebsiella_oxytoca': ['gyrA', 'parC'], 
				'Klebsiella_pneumoniae': ['acrR', 'arnC', 'cirA', 'crrB', 'ftsI', 'gyrA', 'lamB', 'lapB', 'lpxM', 'mgrB', 
								'ompK35', 'ompK36', 'oqxR', 'parC', 'phoP', 'phoQ', 'pmrA', 'pmrB', 'ramR', 'rpsJ'], 
				'Neisseria_gonorrhoeae': ['folP', 'gyrA', 'gyrB', 'mtrR', 'parC', 'parE', 'penA', 'ponA', 'porB1b', 
								'rplD', 'rplV', 'rpoB', 'rpoD', 'rpsE', 'rpsJ'], 
				'Neisseria_meningitidis': ['gyrA', 'rpoB'], 
				'Pseudomonas_aeruginosa': ['amgS', 'ampD', 'ampR', 'cmrA', 'colR', 'colS', 'cprS', 'czcS', 'dacB', 'ftsI', 
								'fusA1', 'glpT', 'gyrA', 'gyrB', 'mexB', 'mexD', 'mexR', 'mexT', 'mexZ', 'nalC', 'nalD', 
								'nfxB', 'oprD', 'parC', 'parE', 'parR', 'parS', 'phoP', 'phoQ', 'pmrA', 'pmrB', 'rplB'], 
				'Salmonella': ['acrB', 'folP', 'gyrA', 'gyrB', 'parC', 'parE', 'pmrA', 'pmrB', 'ramR', 'soxR', 'soxS'], 
				'Serratia_marcescens': ['gyrA'], 
				'Staphylococcus_aureus': ['acrB', 'cls', 'dfrB', 'fexA', 'folP', 'fusA', 'fusE', 'gdpP', 'glpT', 'gyrA', 
								'gyrB', 'ileS', 'mprF', 'murA', 'parC', 'parE', 'pbp2', 'pbp4', 'pgsA', 'rplC', 'rpoB', 
								'rpoC', 'rpsJ', 'uhpT', 'walK'], 
				'Staphylococcus_pseudintermedius': ['grlA', 'gyrA', 'rpoB'], 
				'Streptococcus_agalactiae': ['pbp2x'], 
				'Streptococcus_pneumoniae': ['cdsA', 'parC', 'rplD'], 
				'Streptococcus_pyogenes': ['folP', 'pbp2x'], 
				'Vibrio_cholerae': ['gyrA', 'parC', 'parE'], 
				'Vibrio_parahaemolyticus': ['gyrA', 'parC'], 
				'Vibrio_vulnificus': ['gyrA', 'parC'],
				'Not_specified': []
				}
	if gene in gene_dic[organism]:
		return(True)
	else:
		return(False)
		

def option_settings():
	parser = argparse.ArgumentParser(description='run and summarize amrfinder results')
	parser.add_argument(
		'-l', '--list',
		type = str,
		dest = 'input_list',
		default = '',
		help = 'strain<TAB>fasta<TAB>organism<TAB>plus'
	) 
	parser.add_argument(
		'-r', '--results',
		type = str,
		dest = 'results_file',
		default = '',
		help = 'Results file generated by this program'
	) 
	parser.add_argument(
		'-i', '--identity',
		type = str,
		dest = 'seq_identity',
		default = '0.7',
		help = 'sequence identity'
	) 
	parser.add_argument(
		'-o', '--out',
		type = str,
		dest = 'outfile',
		required = True,
		help = 'prefix of out put file'
	) 
	parser.add_argument(
		'--num_process',
		type = int,
		dest = 'the_number_of_process',
		default = 4,
		help = 'The number of process (default = 4)'
	) 
	parser.add_argument(
		'--transpose',
		dest = 'transpose',
		action="store_true",
		default = False,
		help = 'The Transpose option swaps the gene and strain names in the Excel output.'
	)
	args = parser.parse_args()
	listfiles = args.input_list
	resultsfile = args.results_file
	seq_ident = args.seq_identity
	out_name = args.outfile
	num_process = args.the_number_of_process
	transpose = atgs.transpose
	return(listfiles, resultsfile, seq_ident, out_name, num_process, transpose)

if __name__ == "__main__":
	listfiles, resultsfile, seq_ident, out_name, num_process, transpose = option_settings()

	if listfiles == '' and resultsfile == '':
		print('-l or -r option is required')
		sys.exit()

	fasta_list = []
	manager = Manager()
	results_dic = manager.dict()
	results_text_dic = manager.dict()
	strain_list = []
	run_finder_list = []

	if resultsfile != '': #2022/4/8
		resultfile_dic, resultfile_strain_list = amr_resultsfile(resultsfile)
		for key, values in resultfile_dic.items():
			results_dic[key] = values
	else:
		resultfile_strain_list = []

	if listfiles != '':
		with open(listfiles, 'r') as f:
			fasta_list = f.read().rstrip().split("\n")
		file_list = []
		for each in fasta_list:
			each_split = each.split('\t')
			if len(each_split) == 2:
				file_list.append([each_split[0], each_split[1], seq_ident, 'Not_specified', ''])
			elif len(each_split) == 3:
				file_list.append([each_split[0], each_split[1], seq_ident, each_split[2], ''])
			elif len(each_split) >= 4 and each_split[3] == 'plus':
				file_list.append([each_split[0], each_split[1], seq_ident, each_split[2], '--plus'])
			strain_list.append(each.split('\t')[0])
			run_finder_list.append(each.split('\t')[0])
		pool = Pool(num_process)	
		pool.map(amrfinder, range(len(run_finder_list)))
		pool.close()
		
	total_strain_list = resultfile_strain_list + strain_list #2023/6/9
	print(resultfile_strain_list)
	
	verInfo_dic = amrfinder_version()
	amr2excel(results_dic, out_name, total_strain_list, verInfo_dic, seq_ident, transpose)

	if listfiles != '':
		amr2txt(resultsfile, results_text_dic, strain_list, out_name + '_amrfinder')
