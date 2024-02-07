#!/usr/bin/python3
# -*- coding:utf-8 -*-

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

def amrfinder(strain): # "amrfinder" function is depending on "run_amrfinder'
	results_list = []
	amrfinder_command = ['amrfinder', '-n', file_list[strain][1], '-i', file_list[strain][2]]
	res = subprocess.run(amrfinder_command, stdout=PIPE)
	amr_list = res.stdout.decode('utf8').rstrip().split("\n")
	for amr_line in amr_list:
		amr_line_list = amr_line.split('\t')
		if amr_line_list[0] != 'Protein identifier':
			results_list.append(amr_summary(amr_line))
	results_dic[file_list[strain][0]] = results_list
	results_text_dic[file_list[strain][0]] = res.stdout.decode('utf8')

def amr_summary(line): # 2022/4/8
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
	prefix = ''
	qry_word = gene_symbol
	if len(gene_symbol) > 3:
		if gene_symbol[0:3] == 'bla':
			prefix = 'bla'
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
	if prefix == 'bla' and len(identifier) >= 3 and identifier[0:3].lower() != 'bla':
		identifier = prefix + identifier
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

def amr2excel(results_dic, out_name, strain_list): #2023/6/9
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
	gene_list = sorted(gene_list, key=str.lower) # 2023/4/27
	gene_info_list = sorted(gene_info_list, key=lambda x: x[0].lower()) # 2023/4/27
	gene_info_df = pd.DataFrame(gene_info_list, columns = 
		['Gene symbol' , 'Protein name' , 'Class' , 'Subclass', 'Closest protein'])
	num_strain = len(results_dic)
	num_gene = len(gene_list)

	df_gene_table = pd.DataFrame(np.zeros((num_strain, num_gene), dtype = int), 
		columns = gene_list, index = strain_list)
	df_cov_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list)
	df_ident_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list)
	df_contig_table = pd.DataFrame(np.zeros((num_strain, num_gene)), 
		columns = gene_list, index = strain_list).astype('object')

	for key in results_dic:
		for each in results_dic[key]:
			df_gene_table.at[key, each[0]] = df_gene_table.at[key, each[0]] + 1
			df_cov_table.at[key, each[0]] = float(each[5])
			df_ident_table.at[key, each[0]] = float(each[6])
			df_contig_table.at[key, each[0]] = each[7]

	print(df_gene_table)

	with pd.ExcelWriter(out_name + '_amrfinder.xlsx') as writer:
		df_gene_table.to_excel(writer, sheet_name='summary')
		df_cov_table.to_excel(writer, sheet_name='coverage')
		df_ident_table.to_excel(writer, sheet_name='seq_identity')
		df_contig_table.to_excel(writer, sheet_name='contig_id')
		gene_info_df.to_excel(writer, sheet_name='gene_info')

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

def option_settings():
	parser = argparse.ArgumentParser(description='run and summarize amrfinder results')
	parser.add_argument(
		'-l', '--list',
		type = str,
		dest = 'input_list',
		default = '',
		help = 'strain<TAB>fasta'
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
	args = parser.parse_args()
	listfiles = args.input_list
	resultsfile = args.results_file
	seq_ident = args.seq_identity
	out_name = args.outfile
	num_process = args.the_number_of_process
	return(listfiles, resultsfile, seq_ident, out_name, num_process)

if __name__ == "__main__":
	listfiles, resultsfile, seq_ident, out_name, num_process = option_settings()

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
			file_list.append([each.split('\t')[0], each.split('\t')[1], seq_ident])
			strain_list.append(each.split('\t')[0])
			run_finder_list.append(each.split('\t')[0])
		pool = Pool(num_process)	
		pool.map(amrfinder, range(len(run_finder_list)))
		pool.close()
		
	total_strain_list = resultfile_strain_list + strain_list #2023/6/9
	print(resultfile_strain_list)
		
	amr2excel(results_dic, out_name, total_strain_list)

	if listfiles != '':
		amr2txt(resultsfile, results_text_dic, strain_list, out_name + '_amrfinder')
