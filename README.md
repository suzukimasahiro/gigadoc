# GIGAdoc

## GUI for Microbial Genome Analysis on Docker

GIGAdoc offers a graphical user interface (GUI) for bioinformatics software, facilitating microbial genome analysis on Docker. It's developed for use on Linux but is also compatible with Windows through WSL2. GIGAdoc simplifies the process of using advanced genomic analysis tools by providing a user-friendly interface.

## Latest Updates
- **GIGAdoc icon for Windows executable file is changed from PyInstaller default to new one.**

### **AMRFinder**
- **Support for Organism-Specific Search and "Plus" Option**:
  - The "Organism" option allows taxon-specific screening for known resistance-causing point mutations (e.g., Stx Type for *Escherichia*) and blacklisting of common, non-informative genes.
  - The "Plus" option provides results from "Plus" genes such as virulence factors, stress-response genes, etc.
- **Excel Output Format Changed**:
  - Drug resistance gene names are now aligned vertically for better readability.

### **cgMLST Button Moved**
- The cgMLST button has been moved from the **Typing** tab to the **Phylogeny** tab.
- cgMLST remains in **experimental support**.

### **Software Version Updates**
- **AMRFinder**: Updated from **3.11.20** to **4.0.19**
- **SPAdes**: Updated from **3.15.5** to **4.0.19**
- **fastp**: Updated from **0.23.2** to **0.24.0**
- **chewBBACA** (for cgMLST scheme making): Updated from **3.2.0** to **3.3.10**

---

## Currently Supported Software

GIGAdoc supports an extended list of bioinformatics tools:

- **fastp** and **SPAdes** assembler
- **SNIPPY** and **FastTree**
- **NCBI AMRFinder Plus**
- **MLST**
- **fastANI**
- **cgMLST** (experimental)

These tools cover various aspects of genomic analysis, from pre-processing and assembly to comparative genomics and antimicrobial resistance gene detection.

## 28th February 2024 Update

- **Bug Fixes (28th February 2024)**: Addressed various issues to ensure smoother operation and reliability of GIGAdoc across supported platforms.

## 5th February 2024 Update

- **Default Settings for Folders**: Streamlines workflow by automatically setting up commonly used directories.
- **fastANI Support**: Enables average nucleotide identity (ANI) calculations, facilitating the accurate comparison of microbial genomes.
- **cgMLST Support**: Adds capability for core genome MLST analysis, enhancing strain typing and phylogenetic studies.
- Several small corrections and optimizations have been made to improve performance and user experience.

---

## Installation Guide

### **Windows**
1. **Install WSL2**:
   - Open the terminal as Administrator and enter:
     ```sh
     wsl --install
     ```
   - Reboot your PC and set up your username and password in the Linux terminal.

   - **Increase WSL2 Memory Allocation (If Needed)**:
     - Open a terminal in your home folder (`C:\Users\<your_username>`).
     - Run the following commands to create/edit the `.wslconfig` file:
       ```sh
       echo [wsl2] >> .wslconfig
       echo memory=12GB >> .wslconfig
       ```
     - Adjust the RAM allocation as necessary.

2. **Install Rancher Desktop or Docker Desktop**:
   - Rancher Desktop: [https://rancherdesktop.io/](https://rancherdesktop.io/)
   - Docker Desktop: [https://docs.docker.com/desktop/install/windows-install/](https://docs.docker.com/desktop/install/windows-install/)

3. **Install Python (Optional)**:
   - Download Python from: [https://www.python.org/downloads/](https://www.python.org/downloads/)
   - Install required libraries using pip:
     ```sh
     pip install docker psutil biopython pandas openpyxl
     ```

4. **Get GIGAdoc from GitHub**:
   - Visit: [https://github.com/suzukimasahiro/gigadoc](https://github.com/suzukimasahiro/gigadoc)
   - Download all files from the `bin` directory for the Python script version.
   - Run GIGAdoc:
     ```sh
     python gigadoc.py
     ```
   - **For Windows Executable Version**:
     - Download `gigadoc.exe` and double-click to run.

---

## **System Requirements**

### **Windows**
- Windows 10 or Windows 11
- 16 GB or more RAM (32 GB recommended)
- WSL2
- Rancher desktop or Docker Desktop
- Python (optional)

### **Linux**
- Ubuntu 22.04 LTS (tested)
- 16 GB RAM minimum (32 GB recommended)
- Docker
- Python

### **Mac**
- Not tested (may work using QEMU or Rosetta environment)

---

