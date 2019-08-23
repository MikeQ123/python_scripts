#!/usr/bin/python

import json
import os
import random
import string

######################
smb_creds='/etc/tower/smbcredentials.conf'
backup_path='\\\\\\\\backup01\\\\sql'
backup_folder='\\\\SRV-NAV18-SQL\\\\ASR_PROD\\\\'
survey_name='SBL Deploy ASOR Test Environment'
survey_question='DataBase backup file path'
#####################

cmd = 'smbclient ' + backup_path + ' -D ' + backup_folder + ' -A ' + smb_creds + ' -c ls 2>/dev/null | awk \'{print $1}\' | grep -e \'^\..*$\' -v | grep \'.bak\''
choices = ""

for file in os.popen(cmd).readlines():
    choices = choices + '\n' + backup_path + backup_folder + file.rstrip()
choices = choices[2:]
choices = choices.replace('\\\\','\\')

cmd = 'tower-cli job_template survey -n "' + survey_name + '"'
survey_content = os.popen(cmd).read()

survey_obj = json.loads(survey_content)

for question in survey_obj['spec']:
    if question["question_name"] == survey_question:
       question["choices"] = choices

filename='/tmp/' + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5)) + '.json'
f = open(filename, "w")
f.write(json.dumps(survey_obj, sort_keys=True, indent=4))
f.close()

cmd = 'tower-cli job_template modify -n "' + survey_name + '" --survey-spec=@' + filename + ' --survey-enabled=true'

survey_mod = os.popen(cmd).read()
os.remove(filename)
