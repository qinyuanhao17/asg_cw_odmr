import re

def preprocessor(code):
    code = code.replace('WD', 'awglib.WD')
    code = code.replace('SR', 'awglib.SR')
    code = code.replace('GAmp', 'awglib.GAmp')
    # code = code.replace('UP', 'awglib.UP')        # 直接使用不需要
    # code = code.replace('DOWN', 'awglib.DOWN')    # 直接使用，不需要

    while True:
        p = re.search(r'Sweep\s*[(].*\d+[.]?([num]s)\s*[)]', code, re.M)
        if p == None:
            break
        else:
            code = code[:p.start(1)] + ", unit='{}'".format(p.group(1)) + code[p.end(1):]

    code += '\nawglib.save_in_file([OUT1, OUT2, OUT3, OUT4])'
    return code