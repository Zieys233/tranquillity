import runtime


def init(initalVariablePool:dict):
    initalVariablePool["<runtime>"]["variablePool"]["input"]["internal"] = builtinInput
    initalVariablePool["<runtime>"]["variablePool"]["print"]["internal"] = builtinPrint
    initalVariablePool["<runtime>"]["variablePool"]["str_to_int"]["internal"] = builtinInt
    initalVariablePool["<runtime>"]["variablePool"]["float_to_int"]["internal"] = builtinInt
    initalVariablePool["<runtime>"]["variablePool"]["str_to_float"]["internal"] = builtinFloat
    initalVariablePool["<runtime>"]["variablePool"]["int_to_float"]["internal"] = builtinFloat
    initalVariablePool["<runtime>"]["variablePool"]["to_str"]["internal"] = builtinStr
    initalVariablePool["<runtime>"]["variablePool"]["strlen"]["internal"] = strlen
    initalVariablePool["<runtime>"]["variablePool"]["chr"]["internal"] = numToChar
    initalVariablePool["<runtime>"]["variablePool"]["ord"]["internal"] = getUnicode

def builtinInput(variablePool:dict, currentScope:str) -> int:
    try: content = input()
    except EOFError: return ''
    return content

def builtinPrint(variablePool:dict, currentScope:str) -> int:
    content = runtime.getValue(variablePool, currentScope, "content")[0]['variablePool']['__value']
    if content == None: print("(null)", end=''); return 1
    print(content, end='')
    return len(content)

def builtinInt(variablePool:dict, currentScope:str):
    num = runtime.getValue(variablePool, currentScope, "num")[0]["variablePool"]["__value"]
    if num == None: print("TypeError: Cannot pass in null type"); exit(1)
    return int(float(num))

def builtinFloat(variablePool:dict, currentScope:str):
    num = runtime.getValue(variablePool, currentScope, "num")[0]["variablePool"]["__value"]
    if num == None: print("TypeError: Cannot pass in null type"); exit(1)
    return float(num)

def builtinStr(variablePool:dict, currentScope:str):
    num = runtime.getValue(variablePool, currentScope, "num")[0]["variablePool"]["__value"]
    if num == None: print("TypeError: Cannot pass in null type"); exit(1)
    return str(num)

def strlen(variablePool:dict, currentScope:str):
    content = runtime.getValue(variablePool, currentScope, "content")[0]["variablePool"]["__value"]
    if content == None: print("TypeError: Cannot pass in null type"); exit(1)
    return len(content)

def numToChar(variablePool:dict, currentScope:str):
    num = runtime.getValue(variablePool, currentScope, "num")[0]["variablePool"]["__value"]
    if num == None: print("TypeError: Cannot pass in null type"); exit(1)
    if 0 <= num <= 1114111: return chr(num)
    else: print("ValueError: Unable to convert to character"); exit(1)

def getUnicode(variablePool:dict, currentScope:str):
    char = runtime.getValue(variablePool, currentScope, "char")[0]["variablePool"]["__value"]
    if char == None: print("TypeError: Cannot pass in null type"); exit(1)
    if len(char) != 1: print("ValueError: the parameter of `ord()` must have one and only one character"); exit(1)
    if 0 <= char <= 1114111: return ord(char)
    else: print("ValueError: Unable to get the code point"); exit(1)
