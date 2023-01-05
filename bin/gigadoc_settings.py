#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#             Shared function                                                   #
#                   and                                                         #
#             Tag list for docker images on quay.io/biocontainers               #
#                                                                               #
#################################################################################

# 2022/01/05

import os
import os.path
import webbrowser

def docker_tag(key):
	tags = {
		'date':'20221223',
		'source':'https://bioconda.github.io/index.html',
		'SPAdes':'3.15.5--h95f258a_1',
		'fastp':'0.23.2--h5f740d0_3',
		'SNIPPY':'4.6.0--hdfd78af_2',
		'FastTree':'2.1.11--hec16e2b_1',
		'snp-dists':'0.8.2--h7132678_1',
		'AMRfinder':'3.11.2--h6e70893_0',
		'mlst':'2.23.0--hdfd78af_0',
		'flye':'2.9.1--py39h6935b12_0',
		'pilon':'1.24--hdfd78af_0',
		'unicycler':'0.5.0--py39h2add14b_2',
		'prokka':'1.14.6--pl5321hdfd78af_4',
		'dfast':'1.2.18--h5b5514e_1'
		}
	try:
		tag = tags[key]
	except:
		tag = 'None'
	return(tag)

def user_home():
	if os.name == 'nt':
		win_dir = os.path.expanduser('~').split('\\')
		idir = win_dir[0] + '/' + win_dir[1] + '/' + win_dir[2]
	else:
		idir = os.path.expanduser('~')
	return(idir)

def illumina_raw(file_name):
	file_part = os.path.basename(file_name).split('_')
		### strain_S1_L001_R1_001.fastq.gz (illumina reads)
	sample = ''
	i = len(file_part) - 4
	for j in range(i):
		sample = sample + file_part[j] + '_'
	sample = sample[:-1]
	if file_part[-2] == 'R1':
		file_part[-2] = 'R2'
		R2 = ''
		for each in file_part:
			R2 = R2 + each + '_'
		R2 = R2[:-1]
		R1 = os.path.basename(file_name)
	else:
		file_part[-2] = 'R1'
		R1 = ''
		for each in file_part:
			R1 = R1 + each + '_'
		R1 = R1[:-1]
		R2 = os.path.basename(file_name)
	return([sample, os.path.dirname(file_name), R1, R2])

def illumina_fastp(file_name):
	file_part = os.path.basename(file_name).split('_')
		### strain_R1_fastp.fastq.gz (after fastp trimming)
	sample = ''
	i = len(file_part) - 2
	for j in range(i):
		sample = sample + file_part[j] + '_'
	sample = sample[:-1]
	if file_part[-2] == 'R1':
		file_part[-2] = 'R2'
		R2 = ''
		for each in file_part:
			R2 = R2 + each + '_'
		R2 = R2[:-1]
		R1 = os.path.basename(file_name)
	else:
		file_part[-2] = 'R1'
		R1 = ''
		for each in file_part:
			R1 = R1 + each + '_'
		R1 = R1[:-1]
		R2 = os.path.basename(file_name)
	return([sample, os.path.dirname(file_name), R1, R2])

def jump_to_link(url):
	webbrowser.open_new(url)
