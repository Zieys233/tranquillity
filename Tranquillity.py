"""
Belong to WorldplyStudio
Author : Robot_Steve
==========================
You can study the principle of Tranquility;
You can also create your own programming language.
However, I forbid you to use its source code for personal gain!
==========================
你可以学习Tranquillity的工作原理；
您还可以创建自己的编程语言。
但是，我禁止你使用它的源代码谋求私利！
"""

import sys

""" 命令行参数接收 """
filename = ""
try:
    filename = sys.argv[1]
except:
    print("FileParameterSetError(文件参数设置异常)")

f = None
try:
    """ 打开源码文件 """
    f = open(filename, "rt", encoding="utf-8")
except:
    print("FileError(文件异常)")
else:
    """ 文件位置 """
    FILEPATH = list(filename)
    if "\\" in FILEPATH:
        while FILEPATH[-1] != "\\":
            FILEPATH.pop()
        FILEPATH2 = ""
        for i in FILEPATH:
            FILEPATH2 += i
        FILEPATH = FILEPATH2
    else:
        FILEPATH = ""

    """ 初步解析 """
    textread = f.read()
    f.close()
    cmds_error = textread.split("\n")
    cmds_error.pop()
    textread = textread.replace("\t","    ")

    # 语法错误侦测
    checks = list(textread.replace(" ",""))
    linenum = 0
    syntaxerror = False
    while "\n" in checks:
        endnum = checks.index("\n")
        if (checks[endnum-1]==";") or (checks[endnum-1]=="{") or (checks[endnum-1]=="}") or (checks[endnum-1]=="/" and checks[endnum-2]=="*") or (checks[endnum-1]=="\\"):
            linenum += 1
            checks.pop(endnum)
        else:
            syntaxerror = True
            break

    """ 正式运行 """
    textread = textread.replace("\n","")
    commands = list(textread) # 正式的 多行命令及逐字 列表

    """ 目录 """
    pathl = list(sys.argv[0])
    path = ""
    if "\\" in pathl or "/" in pathl:
        while pathl[-1] != "\\" and pathl[-1] != "/":
            pathl.pop()

        for i in pathl: path += i
    else:
        path = "./"

    """
        全局变量存储字典:
            变量名 : [变量范围, 变量类型, 变量值]
        局部变量存储列表 :
            [{}, ... ,      |             {}]
            之前局部变量字典 | 此时局部变量字典
    """
    globalvarsave = {}
    """
     函数存储 :
         函数名 : [函数范围, 函数参数, 函数代码]
    """
    globalfuncsave = {}
    """ 
    异常列表:
        [[异常名称, 异常代码, 异常模块], ...]
    """
    errorlist = []

    """ 命令执行 """
    line = ""
    models = ""

    def get_var(varname, localvarsave, mode="get"):
        """ 局部查找 """
        localdiclen = len(localvarsave) - 1 # 局部变量列表长度
        localfind = False
        while localdiclen != -1: # 逐个字典查找
            if varname in localvarsave[localdiclen]: # 查找
                localfind = True
                if mode == "get":
                    var = localvarsave[localdiclen][varname]
                    return var
                elif mode == "index":
                    return localdiclen
            localdiclen -= 1
        """ 全局查找 """
        if localfind == False:
            if varname in globalvarsave: # 查找
                if mode == "get":
                    var = globalvarsave[varname]
                    return var
                elif mode == "index":
                    return "global"
        """ 查找不存在 """
        return None

    def get_func(funcname, localfuncsave, mode="get"):
        """ 局部查找 """
        localdiclen = len(localfuncsave) - 1  # 列表长度
        localfind = False
        while localdiclen != -1:  # 逐个字典查找
            if funcname in localfuncsave[localdiclen]:  # 查找
                localfind = True
                if mode == "get":
                    funcinfo = localfuncsave[localdiclen][funcname]
                    return funcinfo
                elif mode == "index":
                    return localdiclen
            localdiclen -= 1
        """ 全局查找 """
        if localfind == False:
            if funcname in globalfuncsave:  # 查找
                if mode == "get":
                    funcinfo = globalfuncsave[funcname]
                    return funcinfo
                elif mode == "index":
                    return "global"
        """ 查找不存在 """
        return None

    def analyzing_command(command_list, range, localvarsave, localfuncsave):
        """
        解析单条命令，通常用于解析词法
        commanmd  : 单条命令的list化列表
        :return   : 命令的执行结果
        """
        global globalvarsave
        analytic_element = [] # 解析出的元素
        element =  "" # 单个元素
        """ 解析元素 """
        while command_list != []:
            while command_list[0] == " ":
                    command_list.pop(0)
            if command_list[0] == "'" or command_list[0] == '"':
                """ 解析字符串 """
                symbol = ""
                if command_list[0] == "'":
                    symbol = "'"
                else:
                    symbol = '"'
                command_list.pop(0)
                try:
                    while command_list[0] != symbol:

                        if command_list[0] == "\\" and command_list[1] == "n":
                            command_list.pop(0)
                            command_list.pop(0)
                            element += "\n"
                        elif command_list[0] == "\\" and command_list[1] == "t":
                            command_list.pop(0)
                            command_list.pop(0)
                            element += "\t"
                        elif command_list[0] == "\\" and command_list[1] == "\\":
                            command_list.pop(0)
                            command_list.pop(0)
                            element += "\\"
                        elif command_list[0] == "\\" and command_list[1] == "f":
                            command_list.pop(0)
                            command_list.pop(0)
                            element += "\f"
                        elif command_list[0] == "\\" and command_list[1] == "b":
                            command_list.pop(0)
                            command_list.pop(0)
                            element += "\b"
                        elif command_list[0] == "\\" and (command_list[1] == "'" or command_list[1]=='"'):
                            command_list.pop(0)
                            command_list.pop(0)
                            element += command_list[0]
                        else:
                            element += command_list[0]
                            command_list.pop(0)
                except:
                    return None
                command_list.pop(0)
                element.replace("\\n","\n")
                analytic_element.append(element) # 将字符串存进解析元素
                element = "" # 重设元素
            elif command_list[0] == "[" and command_list[-1] == "]":
                putlist = []
                command_list.pop(0) # 删除 [
                """ 处理单个列表元素 """
                while command_list != []:
                    listelement = [] # 单个元素
                    times = 0
                    while command_list != []: # 收集单个元素
                        if command_list[0] == "[":
                            times += 1
                        elif command_list[0] == "]":
                            if times == 0:
                                break
                            else:
                                times -= 1
                        elif command_list[0] == "," and times == 0:
                            break
                        else:
                            listelement.append(command_list[0])
                            command_list.pop(0)
                    if listelement != []:
                        retelement = analyzing_command(listelement, range, localvarsave, localfuncsave)
                        if retelement != None:
                            putlist.append(retelement)
                        else:
                            return None
                    else:
                        break
                    """ 删除空格和逗号 """
                    while command_list[0] == " " or command_list[0] == ",":
                        command_list.pop(0)
                """ 返回 """
                command_list.pop(0) # 删除 ]
                analytic_element.append(putlist)
            elif command_list[0] == "+" and command_list[1] == "=" or \
                    command_list[0] == "-" and command_list[1] == "=" or \
                    command_list[0] == "*" and command_list[1] == "=" or \
                    command_list[0] == "/" and command_list[1] == "=" or \
                    command_list[0] == "+" or command_list[0] == "-" or \
                    command_list[0] == "*" or command_list[0] == "/":
                """ 符号 """
                if command_list[0] == "+" and command_list[1] == "=":
                    analytic_element.append("+=")
                    command_list.pop(0)
                    command_list.pop(0)
                elif command_list[0] == "-" and command_list[1] == "=":
                    analytic_element.append("-=")
                    command_list.pop(0)
                    command_list.pop(0)
                elif command_list[0] == "*" and command_list[1] == "=":
                    analytic_element.append("*=")
                    command_list.pop(0)
                    command_list.pop(0)
                elif command_list[0] == "/" and command_list[1] == "=":
                    analytic_element.append("/=")
                    command_list.pop(0)
                    command_list.pop(0)
                elif command_list[0] == "+":
                    analytic_element.append("+")
                    command_list.pop(0)
                elif command_list[0] == "-":
                    analytic_element.append("-")
                    command_list.pop(0)
                elif command_list[0] == "*":
                    analytic_element.append("*")
                    command_list.pop(0)
                elif command_list[0] == "/":
                    analytic_element.append("/")
                    command_list.pop(0)
                element =  ""
            else:
                """ 解析非字符串 """
                if "(" in command_list and ")" in command_list:  # 函数
                    command = ""
                    symbolt =  0
                    while command_list != []:
                        if command_list[0] == "(":
                            symbolt += 1
                        elif command_list[0] == ")":
                            if symbolt == 0:
                                command += command_list[0]
                                break
                            else:
                                symbolt -= 1
                        command += command_list[0]
                        command_list.pop(0)
                    " 解析命令 "
                    cmd = list(command)
                    " 函数名称 "
                    funcname = ""
                    while cmd[0] != "(" and cmd != " ":
                        funcname += cmd[0]
                        cmd.pop(0)
                    while cmd[0] == " ":
                        cmd.pop(0)
                    " 检测是否在字典里 "
                    if funcname in globalfuncsave or get_func(funcname, localfuncsave, "index") != None:
                        " 参数检测 "
                        cmd.pop(0)
                        keyword = []
                        string = False
                        str_symbol = ""
                        key = ""
                        symbol_times = 0
                        try:
                            while cmd != []:
                                if cmd[0] == ")":
                                    if symbol_times == 0:
                                        break
                                    else:
                                        symbol_times -= 1
                                if cmd[0] == "'" or cmd[0] == '"':
                                    str_symbol = cmd[0]
                                    if string == False:
                                        string = True
                                    elif string == True and cmd[0] == str_symbol:
                                        string = False
                                    key += cmd[0]
                                    cmd.pop(0)
                                elif cmd[0] == " ":
                                    if string == False:
                                        # 删除空格
                                        while cmd[0] == " ":
                                            cmd.pop(0)
                                    else:
                                        key += cmd[0]
                                        cmd.pop(0)
                                elif cmd[0] == ",":
                                    if string == False:
                                        keyword.append(key)
                                        key = ""
                                    else:
                                        key += cmd[0]
                                    cmd.pop(0)
                                elif cmd[0] == "(":
                                    symbol_times += 1
                                    key += cmd[0]
                                    cmd.pop(0)
                                else:
                                    key += cmd[0]
                                    cmd.pop(0)
                        except:
                            print("SyntaxError(语法异常)")
                            return None
                        keyword.append(key)
                        keywords = {}  # 参数字典
                        if get_func(funcname, localfuncsave) != None:
                            keynames = list(get_func(funcname, localfuncsave)[1].keys())
                        else:
                            keynames = list(globalfuncsave[funcname][1].keys())
                        parpos   = 0
                        """ 参数局部列表 """
                        newlocalvarsave = [{}]
                        """ 分析参数 """
                        while keyword != [] and keyword != ['']:
                            if "=" in keyword[0] and "'" not in keyword[0] and '"' not in keyword[0]:
                                keyname = ""  # 关键字名称
                                keypar = ""  # 关键字参数
                                getkey = list(keyword[0])
                                passn = False
                                while getkey != []:
                                    if getkey[0] != "=":
                                        if passn == False:
                                            keyname += getkey[0]
                                            getkey.pop(0)
                                        else:
                                            keypar += getkey[0]
                                            getkey.pop(0)
                                    else:
                                        passn = True
                                        getkey.pop(0)
                                rets = analyzing_command(list(keypar), range, localvarsave, localfuncsave)
                                if rets == None:
                                    return None
                                else:
                                    keywords[keyname] = rets
                                keyword.pop(0)
                            else:
                                keyname = ""
                                getkey = list(keyword[0])
                                while getkey != []:
                                    keyname += getkey[0]
                                    getkey.pop(0)
                                ret = analyzing_command(list(keyname), range, localvarsave, localfuncsave)
                                if ret == None:
                                    return None
                                else:
                                    keywords[keynames[parpos]] = ret
                                keyword.pop(0)
                                parpos += 1
                        try:
                            cmd.pop(0)
                        except:
                            print("SyntaxError(语法异常)")
                            return None
                        """ 处理参数 """
                        if get_func(funcname, localfuncsave) != None:
                            keys = list(get_func(funcname, localfuncsave)[1].keys())
                        else:
                            keys = list(globalfuncsave[funcname][1].keys())
                        if key != "":
                            nonepar = []  # 需要检测的参数
                            while keys != []:
                                if keys[0] == None:
                                    nonepar.append(keys[0])
                                keys.pop(0)
                            nonepar2 = list(keywords.keys())
                            if len(nonepar) <= len(nonepar2):
                                while nonepar != []:
                                    if nonepar[0] not in nonepar2:
                                        print("ParameterError(参数错误)")
                                        return None
                                    nonepar.pop(0)
                            else:
                                print("ParameterError(参数异常)")
                                return None
                            keyc = list(keywords.keys())
                            while keyc != []:
                                # 改值
                                newlocalvarsave[0][keyc[0]] = [range, "par", keywords[keyc[0]]]
                                keyc.pop(0)
                        " 获取代码并运行代码"
                        if get_func(funcname, localfuncsave) != None:
                            code = list(get_func(funcname, localfuncsave)[2])
                        else:
                            code = list(globalfuncsave[funcname][2])
                        newlocalvarsave.append({})
                        ret  = run(code, funcname, newlocalvarsave, localfuncsave)
                        """ 返回 """
                        if ret == None:
                            return None
                        elif ret == "0042005200450041004b00540048004500500052004f004700520041004d":
                            print("SyntaxError(语法异常)")
                            return  None
                        else:
                            """ 返回 """
                            element = ""
                            analytic_element.append(ret)
                            if cmd != []:
                                command_list = cmd.copy()
                    else:
                        print("NoDifferentError(未定义而未找到异常)")
                        return None
                analytic_ok = False # 是否解析到了 非字符
                while command_list != [] and command_list[0] != " " and command_list[0] not in ["'",'"'] and  command_list[0] != "+" and command_list[0] != "-" and command_list[0] != "*" and command_list[0] != "/":
                    analytic_ok = True
                    element += command_list[0]
                    command_list.pop(0)
                """ 存入解析元素 """
                if analytic_ok == True:
                    """ 检测变量范围 """
                    have = get_var(element, localvarsave, "index")
                    """ 变量值获取 """
                    if have != None: # 如果是变量
                        varbal = get_var(element, localvarsave)[2]
                        analytic_element.append(varbal)
                    else:
                        try:
                            element = int(element) # 如果是整型
                            analytic_element.append(element)
                            element = ""
                        except:
                            try:
                                element = float(element) # 如果是浮点型
                                analytic_element.append(element)
                                element = ""
                            except:
                                print("TypeError(类型异常)123")
                                return None
                    element = ""
            """ 删除空格 """
            while command_list != [] and command_list[0] == " ":
                command_list.pop(0)
        """ 返回结果 """
        if len(analytic_element) == 1:
            # 如果是单个，直接返回单个
            return analytic_element[0]
        else:
            # 如果是多个，先解析再返回
            if len(analytic_element) < 3: # 当个数小于3时，报错
                # 因为如果是多个，则必须个数大于或等于3
                print("SyntaxError(语法异常)")
                return None
            else:
                result = None
                def func(symbol):
                    indexpos = analytic_element.index(symbol)
                    num = None
                    try:
                        if symbol == "+":
                             num = analytic_element[indexpos-1] + analytic_element[indexpos+1]
                        elif symbol == "-":
                            num = analytic_element[indexpos-1] - analytic_element[indexpos+1]
                        elif symbol == "*":
                            num = analytic_element[indexpos-1] * analytic_element[indexpos+1]
                        elif symbol == "/":
                            num = analytic_element[indexpos-1] / analytic_element[indexpos+1]
                        elif symbol == "+=":
                            num = analytic_element[indexpos - 1] + analytic_element[indexpos + 1]
                        elif symbol == "-=":
                            num = analytic_element[indexpos - 1] - analytic_element[indexpos + 1]
                        elif symbol == "*=":
                            num = analytic_element[indexpos - 1] * analytic_element[indexpos + 1]
                        elif symbol == "/=":
                            num = analytic_element[indexpos - 1] / analytic_element[indexpos + 1]
                    except:
                        print("TypeError(类型异常)")
                        return None
                    analytic_element.pop(indexpos-1)
                    analytic_element.pop(indexpos-1)
                    analytic_element.pop(indexpos-1)
                    analytic_element.insert(indexpos-1, num)
                    return True
                while len(analytic_element) != 1:
                    if "*" in analytic_element:
                        if func("*") == None:
                            return None
                    elif "/" in analytic_element:
                        if func("/") == None:
                            return None
                    elif "+" in analytic_element:
                        if func("+") == None:
                            return None
                    elif "-" in analytic_element:
                        if func("-") == None:
                            return None
                    elif "+=" in analytic_element:
                        if len(analytic_element) != 3:
                            print("SyntaxError(语法异常)")
                            return None
                        if func("+=") == None:
                            return None
                    elif "-=" in analytic_element:
                        if len(analytic_element) != 3:
                            print("SyntaxError(语法异常)")
                            return None
                        if func("-=") == None:
                            return None
                    elif "*=" in analytic_element:
                        if len(analytic_element) != 3:
                            print("SyntaxError(语法异常)")
                            return None
                        if func("*=") == None:
                            return None
                    elif "/=" in analytic_element:
                        if len(analytic_element) != 3:
                            print("SyntaxError(语法异常)")
                            return None
                        if func("/=") == None:
                            return None
                """ 返回 """
                result = analytic_element[0]
                return result

    def judage(judagelist, range, localvarsave, localfuncsave):
        """
        判断条件
        judagelist : 需要判断的条件列表
        :return      : 条件为真返回True，否则返回False
        """

        def single(single_list):
            """
            单个条件判断
            single_list 格式 : [条件, 判断符, 条件]
            """
            try:
                factor1 = analyzing_command(list(single_list[0]), range, localvarsave, localfuncsave)
                factor2 = analyzing_command(list(single_list[2]), range, localvarsave, localfuncsave)
            except:
                return None
            if factor1 == None or factor2 == None:
                return None
            if single_list[1] == "==":
                if factor1 == factor2:
                    return True
                else:
                    return False
            if single_list[1] == "!=":
                if factor1 != factor2:
                    return True
                else:
                    return False
            elif single_list[1] == ">":
                if factor1 > factor2:
                    return True
                else:
                    return False
            elif single_list[1] == "<":
                if factor1 < factor2:
                    return True
                else:
                    return False
            elif single_list[1] == ">=":
                if factor1 >= factor2:
                    return True
                else:
                    return False
            elif single_list[1] == "<=":
                if factor1 <= factor2:
                    return True
                else:
                    return False

        if len(judagelist) > 3:
            """ 创建新型判断列表 """
            new_list = []  # 新列表
            new_pack = []
            while judagelist != []:
                if judagelist[0] == "and" or judagelist[0] == "or":
                    new_list.append(new_pack)
                    new_list.append(judagelist[0])
                    new_pack = []
                    judagelist.pop(0)
                else:
                    new_pack.append(judagelist[0])
                    judagelist.pop(0)
            new_list.append(new_pack)
            judagelist = new_list  # 修正旧列表
        else:
            new_list = []
            new_list.append(judagelist)
            judagelist = new_list
        """ 判断 """
        new_list = []  # 新列表
        while judagelist != []:  # 替换条件为True或False
            if judagelist[0] != "and" and judagelist != "or":
                ret = single(judagelist[0])
                new_list.append(ret)  # 将返回的 True或Flase 存入新列表
                judagelist.pop(0)
            else:
                new_list.append(judagelist[0])
                judagelist.pop(0)
        judagelist = new_list  # 重塑
        """ 判断 """
        if len(judagelist) == 1:  # 如果只有一个返回结果
            return judagelist[0]  # 直接返回True或False
        else:
            judage_ret = []  # 返回结果
            while "and" in judagelist or "or" in judagelist:
                """ 检测and """
                try:
                    indexs = judagelist.index("and")  # 得出第一个and的位置
                    judage1 = judagelist[indexs - 1]
                    judage2 = judagelist[indexs + 1]
                    judagelist.pop(indexs)
                    if judage1 == True and judage2 == True:
                        judage_ret.append(True)
                    else:
                        judage_ret.append(False)
                except:
                    indexs = judagelist.index("or")  # 得出第一个or的位置
                    judage1 = judagelist[indexs - 1]
                    judage2 = judagelist[indexs + 1]
                    judagelist.pop(indexs)
                    if judage1 == True and judage2 == True:
                        judage_ret.append(True)
                    else:
                        judage_ret.append(False)
            while judage_ret != []:
                if judage_ret[0] != False:
                    judage_ret.pop(0)
                else:
                    return False
            return True

    def check(name, listname):
        name = list(name)  # 将关键字名称列表化
        listfrom = listname.copy()
        try:
            for i in name:
                if i == listfrom[0]:
                    listfrom.pop(0)  # 删除当前字符
                else:
                    return False
        except:
            return False
        return True

    def run(commands, range, oldvarsave, oldfuncsave, models=None, notfunc=False):
        global line
        """
        变量字典:
            # 介绍
            局部变量列表
            将之前得到的变量字典添加进去,并且最后一个字典为此局部的字典
        局部变量存储列表 :
            [{}, ... ,      |             {}]
            之前局部变量字典 | 此时局部变量字典
        """
        localvarsave = []
        if oldvarsave != None:
            for i in oldvarsave:
                localvarsave.append(i)
        localvarsave.append({})
        """
            函数字典:
                # 介绍
                局部函数列表
                将之前得到的函数字典添加进去,并且最后一个函数为此局部的函数
            函数存储 :
                函数名 : [函数范围, 函数参数, 函数代码]
        """
        localfuncsave = []
        if oldfuncsave != None:
            for i in oldfuncsave:
                localfuncsave.append(i)
        localfuncsave.append({})
        """ 逐句执行命令 """
        while commands != []:
            # 内置测试用
            if check("PRINTSRC", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                command = ""  # 命令
                while commands[0] != ";":
                    command += commands[0]
                    commands.pop(0)
                commands.pop(0)
                command = list(command)  # list化
                """ 解析命令 """
                ret = analyzing_command(command, range, localvarsave, localfuncsave)  # 解析
                if ret == None:
                    return None
                print(ret) # 打印信息
            elif check("EGG", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands != [] and commands[0] != ";":
                    commands.pop(0)
                if commands == []:
                    print("SyntaxError(语法异常)")
                    return None
                """ 处理 """
                if commands[0] != ";":
                    print("SyntaxError(语法异常)")
                else:
                    commands.pop(0)
                print("愿Tranquillity有所成就，\n希望他不负我的期望!\n也感谢你的使用，Ty感谢有你.")
            elif check("INTVAR", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                name = ""
                newname = ""
                while commands[0] != " ":
                    name += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                while commands[0] != ";":
                    newname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                """ 解析命令 """
                num = get_var(name, localvarsave)[2]
                try:
                    localvarsave[-1][newname] = [range, "var", int(num)]
                except:
                    errorlist.append(["TypeError(类型异常)", line, models])
                    return None
            elif check("STRVAR", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                name = ""
                newname = ""
                while commands[0] != " ":
                    name += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                while commands[0] != ";":
                    newname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                """ 解析命令 """
                num = get_var(name, localvarsave)[2]
                try:
                    localvarsave[-1][newname] = [range, "var", str(num)]
                except:
                    errorlist.append(["TypeError(类型异常)", line, models])
                    return None
            elif check("FLOATVAR", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                name = ""
                newname = ""
                while commands[0] != " ":
                    name += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                while commands[0] != ";":
                    newname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                """ 解析命令 """
                num = get_var(name, localvarsave)[2]
                try:
                    localvarsave[-1][newname] = [range, "var", float(num)]
                except:
                    errorlist.append(["TypeError(类型异常)", line, models])
                    return None
            elif check("SYSTEM_INPUT", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 内容 """
                # 提示信息，必须为字符串
                ret = ""
                while commands[0] != " ":
                    ret += commands[0]  # 将 命令 的 字符 添加进 ret
                    commands.pop(0)
                ret = list(ret)
                while commands[0] == " ":
                    commands.pop(0)
                # 储存变量的名称
                varname = ""
                while commands[0] != ";":
                    varname += commands[0]  # 将 命令 的 字符 添加进 ret
                    commands.pop(0)
                commands.pop(0)
                """ 解析 """
                rets = analyzing_command(ret, range, localvarsave, localfuncsave)
                if rets != None and type(rets) == str:
                    putinfo = input(rets)
                    localvarsave[-1][varname] = [range, "var", putinfo]
                else:
                    errorlist.append(["TypeError(类型异常)", line, models])
                    return None
            elif check("GET_ELEMENT", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                list_name = ""  # 列表名称
                while commands[0] != " ":
                    list_name += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                indexnum = ""  # 列表索引
                while commands[0] != " ":
                    indexnum += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                name = ""  # 存放变量名称
                while commands[0] != ";":
                    name += commands[0]
                    commands.pop(0)
                commands.pop(0)
                indexnum = analyzing_command(list(indexnum), range, localvarsave, localfuncsave)
                if indexnum == None:
                    return None
                try:
                    indexnum = int(indexnum)
                except:
                    print("TypeError(类型异常)")
                    return None
                """ 解析命令 """
                if get_var(list_name, range, "check") != 0:
                    var = None
                    try:
                        var = analyzing_command(list(list_name), range, localvarsave, localfuncsave)[indexnum]
                    except:
                        print("IndexError(索引异常)")
                        return None
                    return var
            elif check("APPEND_ELEMENT", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                list_name = ""  # 列表名称
                while commands[0] != " ":
                    list_name += commands[0]
                    commands.pop(0)
                while commands[0] == " ":
                    commands.pop(0)
                item = ""  # 列表索引
                while commands[0] != ";":
                    item += commands[0]
                    commands.pop(0)
                commands.pop(0)
                item = analyzing_command(list(item), range, localvarsave, localfuncsave)
                if item == None:
                    return None
                """ 解析命令 """
                listindex = get_var(list_name, localvarsave)
                localvarsave[-1][list_name] = [range, "var", listindex.append(item)]
            elif check("READ", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                filepath = ""
                while commands[0] != " ":
                    filepath += commands[0]
                    commands.pop(0)
                filepath = analyzing_command(list(filepath), range, localvarsave, localfuncsave)  # 文件路径
                if filepath == None:
                    errorlist.append(["TypeError(类型异常)", line, models])
                while commands[0] == " ":
                    commands.pop(0)
                putvarname = ""  # 存放的名称
                while commands[0] != ";":
                    putvarname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                """ 存放 """
                text = ""
                try:
                    f = open(FILEPATH + filepath, "rt", encoding="utf-8")
                    text = f.read()
                    f.close()
                except:
                    errorlist.append(["FileNotFoundError(文件不能被找到异常)", line, models])
                    return None
                localvarsave[-1][putvarname] = [range, "var", text]
            elif check("WRITE", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                filepath = ""
                while commands[0] != " ":
                    filepath += commands[0]
                    commands.pop(0)
                filepath = analyzing_command(list(filepath), range, localvarsave, localfuncsave)  # 文件路径
                if filepath == None:
                    errorlist.append(["TypeError(类型异常)", line, models])
                while commands[0] == " ":
                    commands.pop(0)
                writetext = ""
                while commands[0] != ";":
                    writetext += commands[0]
                    commands.pop(0)
                writetext = analyzing_command(list(writetext), range, localvarsave, localfuncsave)  # 写入的内容
                commands.pop(0)
                """ 写入 """
                try:
                    f = open(FILEPATH + filepath, "w", encoding="utf-8")
                    f.write(writetext)
                    f.close()
                except:
                    errorlist.append(["FileNotFoundError(文件不能被找到异常)", line, models])
                    return None
            # 常用
            elif commands[0] == " ":
                # 删除空行
                commands.pop(0)
            elif commands[0] == "/" and commands[1] == "*":
                line = ""
                commandlists = commands.copy()
                while commandlists[0] != "*" and commandlists[0] != "/":
                    line += commandlists[0]
                    commandlists.pop(0)
                commands.pop(0)
                commands.pop(0)
                while 1:
                    # 去掉注释部分
                    if commands[0] == "*" and commands[1] == "/":
                        break
                    commands.pop(0)
                commands.pop(0)
                commands.pop(0)
            elif check("var", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                ret = ""
                while commands[0] != ";":
                    ret += commands[0]  # 将 命令 的 字符 添加进 ret
                    commands.pop(0)
                commands.pop(0)  # 删除 分号
                ret = list(ret)
                """ 解析部分:变量名 """
                valuename = ""
                while (ret[0] != "=") and (ret[0] != "+" and ret[1] != "=") and (ret[0] != " ") \
                        and (ret[0] != "-" and ret[1] != "=") and (ret[0] != "*" and ret[1] != "=") \
                        and (ret[0] != "/" and ret[1] != "="):  # 获取变量名
                    valuename += ret[0]
                    ret.pop(0)
                if models != None:
                    valuename = models + "." + valuename
                """ 删除空格 """
                while ret[0] == " ":
                    ret.pop(0)
                """ 符号 """
                if ret[0] == "=":
                    ret.pop(0)
                    """ 删除空格 """
                    while ret[0] == " ":
                        ret.pop(0)
                elif ret[0] == "+" and ret[1] == "=":
                    ret = list(valuename) + ret
                elif ret[0] == "-" and ret[1] == "=":
                    ret = list(valuename) + ret
                elif ret[0] == "*" and ret[1] == "=":
                    ret = list(valuename) + ret
                elif ret[0] == "/" and ret[1] == "=":
                    ret = list(valuename) + ret
                """ 分析值 """
                value = analyzing_command(ret, range, localvarsave, localfuncsave)
                if value != None:
                    """ 
                    存储变量值: 
                        变量名 : [变量范围, 变量类型, 变量值]
                    """
                    if range == "global" or notfunc == False:
                        globalvarsave[valuename] = [range, "var", value]
                    else:
                        localvarsave[-1][valuename] = [range, "var", value]
                    # print("System: Add Value, now:", varsave)
                else:
                    return None
            # elif check("global", commands) == True:
            #     line = ""
            #     commandlists = commands.copy()
            #     while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
            #         line += commandlists[0]
            #         commandlists.pop(0)
            #     """ 删除关键字 """
            #     while commands[0] != " ":
            #         commands.pop(0)
            #     commands.pop(0)
            #     """ 命令部分 """
            #     globalname = ""  # 需要全局化的变量
            #     while commands[0] != ";":
            #         globalname += commands[0]
            #         commands.pop(0)
            #     commands.pop(0)
            #     """ 运行 """
            #     if get_var(globalname, range, "check") != 0:
            #         indexnum = get_var(globalname, range, "index")
            #         if varsave[indexnum][1][1] != "par":
            #             varsave[indexnum][1][0] = "global"
            #         else:
            #             print("ParameterCannotBeGlobal(参数无法全局化)")
            #             return None
            #     else:
            #         print("NoDiffernrtError(未定义而未找到异常)")
            #         return None
            elif check("while", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                command = ""
                while commands != [] and commands[0] != "{":
                    command += commands[0]
                    commands.pop(0)
                command = list(command)
                if commands[0] != "{":
                    print("SyntaxError(语法异常)")
                    return None
                commands.pop(0)
                """ 解析判断条件 """
                factors = []
                facstr = ""
                while command != []:
                    if command[0] != " ":  # 非空格
                        facstr += command[0]
                        command.pop(0)
                    else:  # 添加
                        while command != [] and command[0] == " ":  # 删除空格
                            command.pop(0)
                        factors.append(facstr)
                        facstr = ""
                """ 代码获取 """
                code = []  # 代码
                symbol = 0  # 意外的 { 符号个数
                try:
                    while 1:  # 获取代码
                        if commands[0] == "{":
                            symbol += 1
                            code.append(commands[0])
                        elif commands[0] == "}" and symbol > 0:
                            symbol -= 1
                            code.append(commands[0])
                        elif commands[0] == "}" and symbol == 0:
                            break
                        else:
                            code.append(commands[0])
                        commands.pop(0)
                except:
                    print("SyntaxError(语法异常)")
                    return None
                commands.pop(0)  # 删除 } 符号
                """ 条件判断 """
                ret1 = judage(factors.copy(), range, localvarsave, localfuncsave)
                if ret1 == None:
                    print("SyntaxError(语法异常)")
                    return None
                while ret1 == True:
                    retcode = run(code.copy(), range, localvarsave, localfuncsave, notfunc=False)
                    if retcode != None:
                        ret1 = judage(factors.copy(), range, localvarsave, localfuncsave)
                        if ret1 == None:
                            print("SyntaxError(语法异常)")
                            return None
                        if retcode == "0042005200450041004b00540048004500500052004f004700520041004d":
                            break
                    else:
                        return None
            elif check("break", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != ";":
                    commands.pop(0)
                commands.pop(0)
                """ 跳出 """
                return "0042005200450041004b00540048004500500052004f004700520041004d"
            elif check("if", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 判读结果 """
                judageret = False
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 命令部分 """
                command = ""
                while commands[0] != "{":
                    command += commands[0]
                    commands.pop(0)
                command = list(command)
                commands.pop(0)
                """ 解析判断条件 """
                factors = []
                facstr = ""
                while command != []:
                    if command[0] != " ":  # 非空格
                        facstr += command[0]
                        command.pop(0)
                    else:  # 添加
                        while command != [] and command[0] == " ":  # 删除空格
                            command.pop(0)
                        factors.append(facstr)
                        facstr = ""
                """ 代码获取 """
                code = []  # 代码
                symbol = 0  # 意外的 { 符号个数
                while 1:  # 获取代码
                    if commands[0] == "{":
                        symbol += 1
                        code.append(commands[0])
                    elif commands[0] == "}" and symbol > 0:
                        symbol -= 1
                        code.append(commands[0])
                    elif commands[0] == "}" and symbol == 0:
                        break
                    else:
                        code.append(commands[0])
                    commands.pop(0)
                commands.pop(0)  # 删除 } 符号
                """ 条件判断 """
                ret1 = judage(factors, range, localvarsave, localfuncsave)
                if ret1 == None:
                    print("SyntaxError(语法异常)")
                    return None
                judageret = ret1
                if ret1 == True:
                    retcode = run(code, range, localvarsave, localfuncsave, notfunc=False)
                    if retcode == None:
                        return None
                    elif retcode == "0042005200450041004b00540048004500500052004f004700520041004d":
                        return "0042005200450041004b00540048004500500052004f004700520041004d"
                while commands != [] and commands[0] == " ":
                    commands.pop(0)
                while check("elif", commands) == True:
                    if judageret == False:
                        line = ""
                        commandlists = commands.copy()
                        while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                            line += commandlists[0]
                            commandlists.pop(0)
                        """ 删除关键字 """
                        while commands[0] != " ":
                            commands.pop(0)
                        commands.pop(0)
                        """ 命令部分 """
                        command = ""
                        while commands[0] != "{":
                            command += commands[0]
                            commands.pop(0)
                        command = list(command)
                        commands.pop(0)
                        """ 解析判断条件 """
                        factors = []
                        facstr = ""
                        while command != []:
                            if command[0] != " ":  # 非空格
                                facstr += command[0]
                                command.pop(0)
                            else:  # 添加
                                while command != [] and command[0] == " ":  # 删除空格
                                    command.pop(0)
                                factors.append(facstr)
                                facstr = ""
                        """ 代码获取 """
                        code = []  # 代码
                        symbol = 0  # 意外的 { 符号个数
                        while 1:  # 获取代码
                            if commands[0] == "{":
                                symbol += 1
                                code.append(commands[0])
                            elif commands[0] == "}" and symbol > 0:
                                symbol -= 1
                                code.append(commands[0])
                            elif commands[0] == "}" and symbol == 0:
                                break
                            else:
                                code.append(commands[0])
                            commands.pop(0)
                        commands.pop(0)  # 删除 } 符号
                        """ 条件判断 """
                        ret2 = judage(factors, range, localvarsave, localfuncsave)
                        if ret2 == None:
                            print("SyntaxError(语法异常)")
                            return None
                        judageret = ret2
                        if ret2 == True:
                            retcode = run(code, range, localvarsave, localfuncsave, models, notfunc=False)
                            if retcode == None:
                                return None
                            while commands != [] and commands[0] == " ":
                                commands.pop(0)
                            while check("elif", commands) == True:
                                num = -1
                                while commands != []:
                                    if commands[0] == "{":
                                        num += 1
                                    elif commands[0] == "}":
                                        if num == 0:
                                            break
                                        else:
                                            num -= 1
                                    commands.pop(0)
                                commands.pop(0)
                            while commands != [] and commands[0] == " ":
                                commands.pop(0)
                            if retcode == "0042005200450041004b00540048004500500052004f004700520041004d":
                                return "0042005200450041004b00540048004500500052004f004700520041004d"
                    else:
                        while check("elif", commands) == True:
                            num = -1
                            while commands != []:
                                if commands[0] == "{":
                                    num += 1
                                elif commands[0] == "}":
                                    if num == 0:
                                        break
                                    else:
                                        num -= 1
                                commands.pop(0)
                            commands.pop(0)
                    while commands != [] and commands[0] == " ":
                        commands.pop(0)
                if check("else", commands) == True:
                    if judageret == False:
                        line = ""
                        commandlists = commands.copy()
                        while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                            line += commandlists[0]
                            commandlists.pop(0)
                        """ 删除关键字 """
                        while commands[0] != " ":
                            commands.pop(0)
                        commands.pop(0)
                        """ 命令部分 """
                        while commands[0] == " ":
                            commands.pop(0)
                        commands.pop(0)
                        """ 代码获取 """
                        code = []  # 代码
                        symbol = 0  # 意外的 { 符号个数
                        while 1:  # 获取代码
                            if commands[0] == "{":
                                symbol += 1
                                code.append(commands[0])
                            elif commands[0] == "}" and symbol > 0:
                                symbol -= 1
                                code.append(commands[0])
                            elif commands[0] == "}" and symbol == 0:
                                break
                            else:
                                code.append(commands[0])
                            commands.pop(0)
                        commands.pop(0)  # 删除 } 符号
                        """ 运行 """
                        retcode = run(code, range, localvarsave, localfuncsave, models)
                        if retcode == None:
                            return None
                        elif retcode == "0042005200450041004b00540048004500500052004f004700520041004d":
                            return "0042005200450041004b00540048004500500052004f004700520041004d"
                    else:
                        num = -1
                        while commands != []:
                            if commands[0] == "{":
                                num += 1
                            elif commands[0] == "}":
                                if num == 0:
                                    break
                                else:
                                    num -= 1
                            commands.pop(0)
                        commands.pop(0)
            elif check("def", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 名称部分 """
                name = ""
                while commands[0] != "(":
                    name += commands[0]
                    commands.pop(0)
                commands.pop(0)
                if models != None:
                    name = models + "." + name
                """ 关键字 """
                keyword = []
                key = ""
                while commands[0] != ")":
                    if commands[0] == " ":
                        # 删除空格
                        while commands[0] == " ":
                            commands.pop(0)
                    elif commands[0] == ",":
                        commands.pop(0)
                        keyword.append(key)
                        key = ""
                    else:
                        key += commands[0]
                        commands.pop(0)
                keyword.append(key)
                keywords = {}  # 新列表
                while keyword != []:
                    if "=" in keyword[0]:
                        keyname = ""  # 关键字名称
                        keypar = ""  # 关键字参数
                        getkey = list(keyword[0])
                        passn = False
                        while getkey != []:
                            if getkey[0] != "=":
                                if passn == False:
                                    keyname += getkey[0]
                                    getkey.pop(0)
                                else:
                                    keypar += getkey[0]
                                    getkey.pop(0)
                            else:
                                passn = True
                                getkey.pop(0)
                        rets = analyzing_command(list(keypar), range, localvarsave, localfuncsave, notfunc=True)
                        if rets == None:
                            return None
                        keywords[keyname] = rets
                        keyword.pop(0)
                    else:
                        keyname = ""
                        getkey = list(keyword[0])
                        while getkey != []:
                            keyname += getkey[0]
                            getkey.pop(0)
                        keywords[keyname] = None
                        keyword.pop(0)
                commands.pop(0)
                """ 代码获取 """
                commands.pop(0)
                code = []  # 代码
                symbol = 0  # 意外的 { 符号个数
                while 1:  # 获取代码
                    if commands[0] == "{":
                        symbol += 1
                        code.append(commands[0])
                    elif commands[0] == "}" and symbol > 0:
                        symbol -= 1
                        code.append(commands[0])
                    elif commands[0] == "}" and symbol == 0:
                        break
                    else:
                        code.append(commands[0])
                    commands.pop(0)
                commands.pop(0)  # 删除 } 符号
                keywordscopy = keywords.copy()
                # keynames = list(keywords.keys())
                # while keynames != []:
                #     if keynames[0] != "":
                #         if range == "global":
                #             globalvarsave[keynames[0]] = [range, "par", keywords[keynames[0]]]
                #         else:
                #             have = get_var(keynames[0], localvarsave, "index")
                #             if have == "global":
                #                 globalvarsave[keynames[0]] = [range, "par", keywords[keynames[0]]]
                #             else:
                #                 localvarsave[have][keynames[0]] = [range, "par", keywords[keynames[0]]]
                #     keynames.pop(0)
                if range == "global":
                    globalfuncsave[name] = [range, keywordscopy, code]
                else:
                    have = get_func(name, localvarsave, "index")
                    if have == "global":
                        globalfuncsave[name] = [range, keywordscopy, code]
                    else:
                        localfuncsave[0][name] = [range, keywordscopy, code]
            elif check("import", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 检测 """
                modname = ""
                while commands[0] != " ":
                    modname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                newname = ""
                if commands[0] == "a" and commands[1] == "s" and commands[2] == " ":
                    commands.pop(0)
                    commands.pop(0)
                    commands.pop(0)
                else:
                    print("SyntaxError(语法异常)")
                    return None
                while commands[0] != ";":
                    newname += commands[0]
                    commands.pop(0)
                commands.pop(0)
                model = modname
                modname = modname.replace(".", "/")
                """ 检测是否为内部模块 """
                includes = list("model/")
                includetrue = False
                for i in modname:
                    if includes != []:
                        if i == includes[0]:
                            includes.pop(0)
                        else:
                            break
                    else:
                        includetrue = True
                """ 调用模块 """
                if includetrue == True:
                    modname = modname.replace("model/", "")
                    f = open(path + "\\Lib\\" + modname + ".ty", "rt", encoding="utf-8")
                    textread = f.read()
                    f.close()
                    textread = textread.replace("\t", "    ").replace("\n", "")
                    codes = list(textread)
                    if newname == "*":
                        ret = run(codes, "global", localvarsave, localfuncsave)
                        models = models
                        if ret == None:
                            print("ModelCallError(模块调用异常)")
                            return None
                        elif ret == " 0042005200450041004b00540048004500500052004f004700520041004d":
                            print("ModelCallError(模块调用异常)")
                            return None
                    else:
                        ret = run(codes, "global", localvarsave, localfuncsave, newname)
                        if ret == None:
                            print("ModelCallError(模块调用异常)")
                            return None
                        elif ret == " 0042005200450041004b00540048004500500052004f004700520041004d":
                            print("ModelCallError(模块调用异常)")
                            return None
                else:
                    f = open(modname + ".ty", "rt", encoding="utf-8")
                    textread = f.read()
                    f.close()
                    textread = textread.replace("\t", "    ").replace("\n", "")
                    codes = list(textread)
                    if newname == "*":
                        ret = run(codes, "global", localvarsave, localfuncsave)
                        if ret == None:
                            print("ModelCallError(模块调用异常)")
                            return None
                        elif ret == " 0042005200450041004b00540048004500500052004f004700520041004d":
                            print("ModelCallError(模块调用异常)")
                            return None
                    else:
                        ret = run(codes, "global", localvarsave, localfuncsave, newname)
                        if ret == None:
                            print("ModelCallError(模块调用异常)")
                            return None
                        elif ret == " 0042005200450041004b00540048004500500052004f004700520041004d":
                            print("ModelCallError(模块调用异常)")
                            return None
            elif check("return", commands) == True:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 删除关键字 """
                while commands[0] != " ":
                    commands.pop(0)
                commands.pop(0)
                """ 检测 """
                cmd = ""
                while commands[0] != ";":
                    cmd += commands[0]
                    commands.pop(0)
                commands.pop(0)
                rets1 = analyzing_command(list(cmd), range, localvarsave, localfuncsave)
                if rets1 == None:
                    return None
                return rets1
            else:
                line = ""
                commandlists = commands.copy()
                while commandlists != [] and commandlists[0] != ";" and commandlists[0] != "{":
                    line += commandlists[0]
                    commandlists.pop(0)
                """ 检测 """
                cmd = ""
                while commands[0] != ";":
                    cmd += commands[0]
                    commands.pop(0)
                commands.pop(0)
                rets = analyzing_command(list(cmd), range, localvarsave, localfuncsave)
                if rets == None:
                    return None
        return True

    if syntaxerror == False:
        ret = run(commands, "global", {}, {})
        if ret == "0042005200450041004b00540048004500500052004f004700520041004d":
            print("SyntaxError(语法异常)")
        if ret == None:
            print("ErrorLine(错误行数)(Model: " + str(models) + "):\n\t" + str(line))
    else:

        print("ErrorLine(错误行数)(Model: " + str(models) + "):\n\t" + str(cmds_error[linenum]))
