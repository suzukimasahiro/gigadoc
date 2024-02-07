# GIGAdoc
GUI for Microbial Genome Analysis on Docker

GIGAdoc offers a graphical user interface (GUI) for bioinformatics software, facilitating microbial genome analysis on Docker. It's developed for use on Linux but is also compatible with Windows through WSL2. GIGAdoc simplifies the process of using advanced genomic analysis tools by providing a user-friendly interface. The latest version introduces several enhancements, including default settings for folders, support for fastANI and cgMLST, alongside other minor corrections, improving overall usability and functionality.

## Currently Supported Software

GIGAdoc now supports an extended list of bioinformatics tools:

- fastp and SPAdes assembler
- SNIPPY and FastTree
- NCBI AMRFinder Plus
- MLST
- **fastANI** (new)
- **cgMLST** (experimental)

These tools cover various aspects of genomic analysis, from pre-processing and assembly to comparative genomics and antimicrobial resistance gene detection.

## New Features

- **Default Settings for Folders**: Streamlines workflow by automatically setting up commonly used directories.
- **fastANI Support**: Enables average nucleotide identity (ANI) calculations, facilitating the accurate comparison of microbial genomes.
- **cgMLST Support**: Adds capability for core genome MLST analysis, enhancing strain typing and phylogenetic studies.

## Other Improvements

- Several small corrections and optimizations have been made to improve performance and user experience.

## System Requirements

- Windows 10 or Windows 11
- 16 GB or more memory (32 GB or more is recommended)
- WSL2
- Docker Desktop
- Python (optional)

These requirements ensure that GIGAdoc runs smoothly, providing an efficient and seamless analysis experience for microbial genomics research.

