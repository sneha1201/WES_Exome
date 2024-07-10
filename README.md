# WES_Exome
Whole Exome Sequencing analysis from raw data to vcf generation using BCFTOOLS (python script ) 
Requirements : Python is installed in the root .

Data Require
    •  Fastq files ending with _R1.fastq.gz , _R2.fastq.gz 
    • Put both Fastq files in the same folder , where results are also going to save .
    • reference.fasta - This script assumes a reference file as this name only and script and reference file should be in the same directory .

Usage : 

    • Prepare Data : Place compressed Fastq files in a directory 
    • Ensure genome file as reference.fasta in the same directory as of script.
    • Run the script : python3 variant.py /path/to/fastq_files

Example : python3 variant.py fastq_files/

Note : 

    • Check pipeline.log file for the errors 
    • This script is executable in macos , for linux change brew to sudo 
