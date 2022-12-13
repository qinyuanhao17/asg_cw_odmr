"""
For running faster
"""
import os
import sys
import re
import traceback
import py_compile
from awglib import *

# def parse_code(code, out_file, check_mode='cnt'):
#     awglib.set_out_filename(out_file)
#     awglib.set_check_mode(check_mode)

#     if code == None:
#         awglib.log_and_exit('File path error.')
#     elif code == '':
#         awglib.log_and_exit('Empty script.')
    
#     try:
#         OUT1 = None
#         OUT2 = None
#         OUT3 = None
#         OUT4 = None
#         code = code.replace('WD', 'awglib.WD')
#         code = code.replace('SR', 'awglib.SR')
#         code = code.replace('GAmp', 'awglib.GAmp')
#         # code = code.replace('UP', 'awglib.UP')        # 直接使用不需要
#         # code = code.replace('DOWN', 'awglib.DOWN')    # 直接使用，不需要
#         code += '\nawglib.save_in_file([OUT1, OUT2, OUT3, OUT4])'
#         # print(code)
#         user_code_exec = compile(code, '', 'exec')
#         exec(user_code_exec)
#     except Exception as err:
#         err_msg = str(err)
#         trcbk = traceback.format_exc(limit=None).split('\n')
#         for l in trcbk[3:]:
#             err_msg += '\n!' + l
#         awglib.log_and_exit(err_msg)


# def main():
if len(sys.argv) >= 3:
    out_file = sys.argv[2]
else:
    out_file = 'awg-temp-file'

if len(sys.argv) >= 4:
    if sys.argv[3] == '-C':
        check_mode = 'cnt'
    elif sys.argv[3] == '-T':
        check_mode = 'trg'
else:
    check_mode = 'cnt'

if len(sys.argv) >= 2:
    script_file = sys.argv[1]
    if os.path.isfile(script_file):
        with open(script_file, encoding='utf-8') as f:
            user_script = f.read()
        user_script = user_script.replace(';', '')
    else:
        user_script = None
else:
    user_script = None
    
# parse_code(user_script, out_file, check_mode)
code = user_script
awglib.set_out_filename(out_file)
awglib.set_check_mode(check_mode)

if code == None:
    awglib.log_and_exit('File path error.')
elif code == '':
    awglib.log_and_exit('Empty script.')

try:
    OUT1, OUT2, OUT3, OUT4 = None, None, None, None
    p_code = preprocessor(code)
    # print(code)
    user_code_exec = compile(p_code, '', 'exec')
    exec(user_code_exec)
    
except Exception as err:
    err_msg = str(err)
    trcbk = traceback.format_exc(limit=None).split('\n')
    lineno = re.search(r'line \d+,', trcbk[3])
    if lineno is not None:
        pos = lineno.span()
        lineno = int(trcbk[3][pos[0]+5:pos[1]-1])
        lines = code.split('\n')
        if lineno < len(lines):
            err_msg += '\n! -> ' + code.split('\n')[lineno - 1]
    for l in trcbk[3:]:
        err_msg += '\n!' + l
    awglib.log_and_exit(err_msg)
