import sys
import subprocess



# implement pip to install PySimpleGUI:
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'pysimplegui'])

# process output with an API in the subprocess module:
reqs = subprocess.check_output([sys.executable, '-m', 'pip',
'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

print(installed_packages)

# use pip to install nltk:
subprocess.check_call([sys.executable, '-m', 'pip', 'install',
'nltk'])

import nltk
nltk.download()

# process output with an API in the subprocess module:
reqs = subprocess.check_output([sys.executable, '-m', 'pip',
'freeze'])
installed_packages = [r.decode().split('==')[0] for r in reqs.split()]

print(installed_packages)