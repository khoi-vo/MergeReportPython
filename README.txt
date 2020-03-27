Read this instruction before using the tool:

This tool has 2 main functions are merging and updating. 
####################################################################################################
The MERGING function receives the input is the directory 
contains the folder of multiple Test Suite Result files, these files are took and merged together. If the optional
output is not specified, the report is generated automatically in the folder reports which locates in the same destination
with the tool, else the report is generated at the desired location.

Note: For the input directory, user should specify the folder which has the only the test set they would like to merge.
For the output directory, user should specify a folder which can be distinguished with the next merging time.

Syntax in cmd: python Main.py -i "INPUT-DIR" -o "OUTPUT-DIR"

####################################################################################################
The UPDATE function receives the first argument is the directory 
contains the folder of reports need to be updated, these files are took and updated. The second argument
is the directory contains the folder of ONE report used for updating.

Note: For the MAIN-DIR, user should specify the folder which has the only the test set they would like to update.

Syntax in cmd: python Main.py -m "MAIN-DIR" -s "SUB-DIR"

####################################################################################################

Syntax in cmd for HELP: python Main.py -h		
