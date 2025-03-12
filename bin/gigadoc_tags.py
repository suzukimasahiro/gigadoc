#!/usr/bin/python3
# -*- coding:utf-8 -*-

#################################################################################
#                                                                               #
#             GIGAdoc, GUI for microbial Genome Analysis on Docker              #
#             Setting data                                                      #
#                   and                                                         #
#             Tag list for docker images on quay.io/biocontainers               #
#                                                                               #
#################################################################################

# 2025/03/12 Update tags
# 2024/02/02 cgMLST support
# 2022/01/05

def docker_tag(key):
	tags = {
		'date':'20250314',
		'source':'https://bioconda.github.io/index.html',
		'SPAdes':'4.1.0--haf24da9_0',
		'fastp':'0.24.0--heae3180_1',
		'SNIPPY':'4.6.0--hdfd78af_2',
		'FastTree':'2.1.11--hec16e2b_1',
		'snp-dists':'0.8.2--h7132678_1',
		'AMRfinder':'4.0.19--hf69ffd2_0',
		'mlst':'2.23.0--hdfd78af_1',
		'flye':'2.9.1--py39h6935b12_0',
		'pilon':'1.24--hdfd78af_0',
		'unicycler':'0.5.0--py39h2add14b_2',
		'prokka':'1.14.6--pl5321hdfd78af_4',
		'dfast':'1.2.18--h5b5514e_1',
		'chewbbaca':'3.3.10--pyhdfd78af_0',
		'prodigal':'2.6.3--h031d066_6',
		'fastani':'1.34--h4dfc31f_1',
		'blast':'2.14.1--pl5321h6f7f691_0'
		}
	try:
		tag = tags[key]
	except:
		tag = 'None'
	return(tag)

##### Previous tags #####
'''
Update 2025/03/12
		'chewbbaca':'3.2.0--pyhdfd78af_0',
		'fastp':'0.23.2--h5f740d0_3',
		'SPAdes':'3.15.5--h95f258a_1',
		'AMRfinder':'3.11.20--h283d18e_0',
Update 2024/02/05
		'AMRfinder':'3.11.2--h6e70893_0',
		'mlst':'2.23.0--hdfd78af_0',
'''
