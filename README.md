# Installation
Run the script "install.bat" to install the required Python libraries
which are specified in the file "requirements.txt".

# Configuring
Specify the changes file, the input and output directories in the "config.json" file.
Remember that backslashes should be escaped (prefixed with another backslash) in JSON.
The input and output directory can be the same, which means the files will be overwritten.
The changes file can be any JSON file which stores a replacement dictionary in the field "changes".

# Warning
If the output directory is distinct from the input directory, the program
will delete its contents entirely before starting to process the files.

# Usage
Run the script "CorpusEditor.bat" to run the application.
The program will apply the changes specified in the changes file
to all morphological analyses of all words the XML files in the input directory
and store the modified XML files in the output directory.

# Note
.bat scripts are sequences of command line commands.
They can usually be executed by clicking on the .bat file
in the file explorer.
If clicking does not work, start the command line,
navigate to the containing directory of the .bat file
and type the name of the file (e. g. install.bat), then click "Enter".
