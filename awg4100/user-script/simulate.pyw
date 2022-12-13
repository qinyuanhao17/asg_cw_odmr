import os
import sys
from subprocess import run

cwd = os.path.abspath(sys.path[0])

_DEBUG = True

if _DEBUG:    
    #script = "w1 = WAVE([0, 1, 2, 3, 4, 5, 6, 7, 8,\n   9, 10, 11, 12, 13, 14, 15,\n 14, 13, 12, 11, 10, 9, 8,\n7, 6, 5, 4, 3, 2, 1, 0, 0])\n#w2 = WAVE('./data.wave')\nw3 = Sin()\nw4 = Gauss()\nw5 = Sin(3)\n    \ns1 = w3(4, MODE_T) + w4(2, MODE_C)\ns2 = w5(2, MODE_T) + w4(1, MODE_C) \\\n\t+ w3(2, MODE_C)\n    \na1 = s1(3, MODE_T) + s2(2, MODE_T)\n    \nOUT1 = a1\nOUT2 = s2\n"
    #lines_user  = script.split('\n')
    with open(os.path.join(cwd, 'script-half.py'), 'r', encoding='utf-8') as f:
        lines_script = f.readlines()
        f.close()

    with open(os.path.join(cwd, sys.argv[1]), 'r', encoding='utf-8') as f:
        lines_user = f.readlines()
    #for l in lines_user:
    #    print(l, end='')
    custom_filename = None
    out_type = sys.argv[2]
else:
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1]) as f:
            lines_user = f.readlines()
    else:
        lines_user = sys.argv[1].replace(';', '\n')
    lines_user  = lines_user.split('\n')
    custom_filename = sys.argv[2]
    out_type = sys.argv[3]
    
    with open(os.path.join(cwd, 'script-half'), 'r', encoding='utf-8') as f:
        lines_script = f.readlines()
        f.close()
    

insert_pos = 0
for l in lines_script:
    lt = l.strip()
    if lt == "@user":
        break
    else:
        insert_pos += 1

new_file = []
for l in lines_script[:insert_pos]:
    new_file.append(l)
for l in lines_user:
    #lt = l.strip()
    #print(lt)
    new_file.append(' '*4 + l + '\n')
if custom_filename is not None:
    lt = ' '*4 + 'filename = "' + custom_filename + '"\n'
    new_file.append(lt)
    #print(lt)
for l in lines_script[insert_pos+1:]:
    new_file.append(l)
 
#for l in new_file:
#    print(l, end='')

file = os.path.join(os.environ['TEMP'], 'odmr-tmp-file')
with open(file, 'w', encoding='utf-8') as f:
    f.writelines(new_file)

if _DEBUG:
    run([os.path.join(cwd, 'python.exe'), file, out_type])
else:
    run([os.path.join(cwd, 'uspyw36.exe'), file, out_type])

#os.remove(file)
