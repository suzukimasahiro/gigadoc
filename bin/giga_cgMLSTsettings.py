#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#             cgMLST Setting data and functions                                 #
#                                                                               #
#################################################################################

# 2025/03/12 Minor update to adapt Ridom scheme support
# 2023/12/06

import os
import os.path
from gigadoc_functions import user_home, chk_dir

def cgmlst_schemes(request):
	# bigsDB https://rest.pubmlst.org/
	schemes_dic = {'Acinetobacter cgMLST v1': 'https://rest.pubmlst.org/db/pubmlst_abaumannii_seqdef/schemes/3', 
					'Bacillus anthracis cgMLST': 'https://rest.pubmlst.org/db/pubmlst_bcereus_seqdef/schemes/2', 
					'Bacillus cereus cgMLST': 'https://rest.pubmlst.org/db/pubmlst_bcereus_seqdef/schemes/5', 
					'Borrelia cgMLST': 'https://rest.pubmlst.org/db/pubmlst_borrelia_seqdef/schemes/3', 
					'Brucella cgMLST': 'https://rest.pubmlst.org/db/pubmlst_brucella_seqdef/schemes/3', 
					'Burkholderia pseudomallei cgMLST': 'https://rest.pubmlst.org/db/pubmlst_bpseudomallei_seqdef/schemes/2', 
					'Campylobacter jejuni-coli cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_campylobacter_seqdef/schemes/4', 
					'Chlamydiales abortus cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_chlamydiales_seqdef/schemes/44', 
					'Chlamydiales trachomatis cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_chlamydiales_seqdef/schemes/42', 
					'Clostridium perfringens cgMLST': 'https://rest.pubmlst.org/db/pubmlst_cperfringens_seqdef/schemes/2', 
					'Dichelobacter cgMLST': 'https://rest.pubmlst.org/db/pubmlst_dnodosus_seqdef/schemes/3', 
					'Escherichia cgMLST': 'https://rest.pubmlst.org/db/pubmlst_escherichia_seqdef/schemes/6', 
					'Haemophilus influenzae cgMLST v1': 'https://rest.pubmlst.org/db/pubmlst_hinfluenzae_seqdef/schemes/56', 
					'Leptospira cgMLST': 'https://rest.pubmlst.org/db/pubmlst_leptospira_seqdef/schemes/4', 
					'Mycobacteroides abscessus cgMLST': 'https://rest.pubmlst.org/db/pubmlst_mabscessus_seqdef/schemes/2', 
					'Human-restricted Neisseria cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_neisseria_seqdef/schemes/72', 
					'Neisseria gonorrhoeae cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_neisseria_seqdef/schemes/62', 
					'Neisseria meningitidis cgMLST v2': 'https://rest.pubmlst.org/db/pubmlst_neisseria_seqdef/schemes/85', 
					'Salmonella cgMLST v2 (Enterobase)': 'https://rest.pubmlst.org/db/pubmlst_salmonella_seqdef/schemes/4', 
					'Salmonella SalmcgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_salmonella_seqdef/schemes/3', 
					'Streptococcus agalactiae cgMLST v1.0': 'https://rest.pubmlst.org/db/pubmlst_sagalactiae_seqdef/schemes/38', 
					'Streptococcus pneumoniae cgMLST': 'https://rest.pubmlst.org/db/pubmlst_spneumoniae_seqdef/schemes/2', 
					'Vibrio parahaemolyticus cgMLST': 'https://rest.pubmlst.org/db/pubmlst_vparahaemolyticus_seqdef/schemes/3', 
					'Xanthomonas citri cgMLST': 'https://rest.pubmlst.org/db/pubmlst_xcitri_seqdef/schemes/1'
					}
	if request == 'key':
		return(list(schemes_dic.keys()))
	else:
		return(schemes_dic[request])

def pubmlst_species(request):
	reference_dic = {'Acinetobacter cgMLST v1': 'Acinetobacter baumannii',
					'Bacillus anthracis cgMLST': 'Bacillus anthracis',
					'Bacillus cereus cgMLST': 'Bacillus cereus',
					'Borrelia cgMLST': 'Borreliella burgdorferi',
					'Brucella cgMLST': 'Brucella melitensis',
					'Burkholderia pseudomallei cgMLST': 'Burkholderia pseudomallei',
					'Campylobacter jejuni-coli cgMLST v1.0': 'Campylobacter jejuni',
					'Chlamydiales abortus cgMLST v1.0': 'Chlamydiales abortus',
					'Chlamydiales trachomatis cgMLST v1.0': 'Chlamydiales trachomatis',
					'Clostridium perfringens cgMLST': 'Clostridium perfringens',
					'Dichelobacter cgMLST': 'Dichelobacter nodosus',
					'Escherichia cgMLST': 'Escherichia coli',
					'Haemophilus influenzae cgMLST v1': 'Haemophilus influenzae',
					'Leptospira cgMLST': 'Leptospira interrogans',
					'Mycobacteroides abscessus cgMLST': 'Mycobacteroides abscessus',
					'Human-restricted Neisseria cgMLST v1.0': 'Neisseria meningitidis',
					'Neisseria gonorrhoeae cgMLST v1.0': 'Neisseria gonorrhoeae',
					'Neisseria meningitidis cgMLST v2': 'Neisseria meningitidis',
					'Salmonella cgMLST v2 (Enterobase)': 'Salmonella enterica',
					'Salmonella SalmcgMLST v1.0': 'Salmonella enterica',
					'Streptococcus agalactiae cgMLST v1.0': 'Streptococcus agalactiae',
					'Streptococcus pneumoniae cgMLST': 'Streptococcus pneumoniae',
					'Vibrio parahaemolyticus cgMLST': 'Vibrio parahaemolyticus',
					'Xanthomonas citri cgMLST': 'Xanthomonas citri'
					}
	return(reference_dic[request])

def prepare_dir(scheme):
	cgmlst_dir = user_home('cgMLSTdir')
	scheme_dir = '/' + scheme.replace(' ', '_')
	chk_dir(cgmlst_dir, '/alleles')
	chk_dir(cgmlst_dir + '/alleles', scheme_dir)
	chk_dir(cgmlst_dir, '/trnfile')
	chk_dir(cgmlst_dir, '/schemes')
	chk_dir(cgmlst_dir, '/out')
	'''
	if os.path.isdir(cgmlst_dir):   ##### cgMLST_dir #####
		pass
	else:
		os.mkdir(cgmlst_dir)
	if os.path.isdir(cgmlst_dir + '/alleles'):
		pass
	else:
		os.mkdir(cgmlst_dir + '/alleles')
	if os.path.isdir(cgmlst_dir + '/alleles/' + scheme_dir):   ##### allelesdir #####
		pass
	else:
		os.mkdir(cgmlst_dir + '/alleles/' + scheme_dir)
	if os.path.isdir(cgmlst_dir + '/trnfile'):   ##### trndir #####
		pass
	else:
		os.mkdir(cgmlst_dir + '/trnfile')
	if os.path.isdir(cgmlst_dir + '/schemes'):   ##### dbdir #####
		pass
	else:
		os.mkdir(cgmlst_dir + '/schemes')
	'''
	#if os.path.isdir(cgmlst_dir + '/schemes/' + scheme_dir):
	#	pass
	#else:
	#	os.mkdir(cgmlst_dir + '/schemes/' + scheme_dir)


def scheme_species(scheme):
	if 'Ridom' in scheme:
		genus = scheme.split('_')[0]
		sp = scheme.split('_')[1]
		return(f"{genus} {sp}")
	else:
		return(pubmlst_species(scheme.replace('_', ' ')))


def cgmlst_files(scheme, mode):
	cgMLST_dir = user_home('cgMLSTdir')
	scheme_dir = '/' + scheme.replace(' ', '_')
	species = scheme_species(scheme).replace(' ', '_')
	#species = cgmlst_reference(scheme)[0]
	if mode == 'cgMLSTdir':
		return(cgMLST_dir)
	elif mode == 'trndir':
		return('/trnfile')
	elif mode == 'ref':
		return(f"{species}_genome.fna")
	elif mode == 'trn':
		return(species + '.trn')
	elif mode == 'allelesdir':
		return('/alleles' + scheme_dir)
	elif mode == 'schemesdir':
		return('/schemes')
	elif mode == 'dbdir':
		return('/schemes' + scheme_dir)
	elif mode == 'outdir':
		return('/out')
	elif mode == 'each_scheme':
		return(scheme_dir)
	else:
		return('ERROR')
