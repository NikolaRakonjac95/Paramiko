import paramiko
from datetime import date
import os
# connect to the remote syslog server
hostname = 'ip address of syslog server'
port = 22
username = 'login username'
password = 'login password'
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname, port, username, password)

# with following command I accomplished to filter just user config logs
stdin, stdout, stderr = ssh.exec_command('cd /var/log/syslogs && zgrep executed pix.log* | grep asa | grep -v pixstby | grep -v ciscoprime | grep -v running | grep executed |grep -v enable | grep -v conf | grep User | grep -v write | grep -v packet | grep -v capture | grep -v clear | grep -v terminal | grep -v ping')
output = stdout.read().decode()
file = open('Firewall_logs.txt','w')
file.write(output)
file.close()

ssh.close()
# editing txt document in order to extract only lines which are readable and applicable on cisco asa firewall
day = date.today()
file_name = "output_1"+"_"+str(day)+".txt"
with open('Firewall_logs.txt', "r") as output, open("temporarly.txt", "w") as new_document:
    output_text = output.readlines()
    start_char = "the '"
    end_char = "' command"
    for line in output_text:
            start_pos = line.find(start_char) + len(start_char)
            end_pos = line.find(end_char, start_pos)
            result = line[start_pos:end_pos]
            result = " ".join(result.split())
            new_document.write(result)
            new_document.write("\n")

# In my situation, nat config logs appear without brackets, so I have to make couple changes in order to correct this
# Also access list configuration appear with "line" mark. This is problem when we have to clear more than one line of access list because when one line is removed, fw do recalculate access-list lines, so follow code will remove "line" from "no access-list ..." configuration  
with open("temporarly.txt", "r") as output, open (file_name, "w") as output_1:
    output_text = output.readlines()
    for i in output_text:
        if i.startswith("nat"):
            old = i.splitlines()[0].split()[1]
            new = "(" + old + ","
            i = i.replace(old, new)
            old = i.splitlines()[0].split()[2]
            new = old + ")"
            i = i.replace(old, new)
            i = " ".join(i.split())
        elif i.startswith("no nat"):
            old = i.splitlines()[0].split()[2]
            new = "(" + old + ","                       
            i = i.replace(old, new)
            old = i.splitlines()[0].split()[3]
            new = old + ")"
            i = i.replace(old, new)
            i = " ".join(i.split())
        elif i.startswith("no access-list") and "line" in i:
            remove = i.splitlines()[0].split()[3]
            i = i.replace(remove, ' ')
            remove = i.splitlines()[0].split()[3]
            i = i.replace(remove, ' ')
            i = " ".join(i.split()) 
        else:
            i = " ".join(i.split())
        output_1.write(i)
        output_1.write("\n")
os.remove("temporarly.txt")
