from sys import exit
from unicodedata import category
from sys import maxunicode
from copy import deepcopy


invalidSymbol = [c for _i in range(maxunicode+1) if category(c:=chr(_i)).startswith('P')]; invalidSymbol.remove('_')

currentLibraryPath = ''
currentRuntimePath = ''

def getSourceCode(path):
    try:
        with open(path, 'r') as f:
            sourceCode = deleteBlankPart(f.read(), 1)
            return sourceCode
    except OSError: print(f"OSError: Can not find '{path}' file"); exit(1)
    except FileNotFoundError: print("OSError: Can not find the source file"); exit(1)
    except IndexError: print("OSError: Missing source file"); exit(1)

def deleteBlankPart(code:str, remainingBlankCount:int):
    _tmp, stringMode, annotationMode, i = '', False, 0, 0
    while i < len(code):
        if (code[i] == '"' or code[i] == '\'') and not annotationMode: 
            if not stringMode: stringMode = code[i]
            elif stringMode == code[i]: stringMode = False
        if not stringMode and not annotationMode and code[i] == '/' and code[i+1] == '/': annotationMode = 1
        if not stringMode and not annotationMode and code[i] == '/' and code[i+1] == '*': annotationMode = 2
        if annotationMode == 1 and not stringMode and code[i] == '\n': annotationMode = 0
        elif annotationMode == 2 and not stringMode and code[i] == '*' and code[i+1] == '/': annotationMode = 0; i += 1
        elif annotationMode == 0: _tmp += code[i]
        i += 1
    if stringMode: print("SyntaxError: incomplete input of string"); exit(1)

    code = _tmp.replace("\t", '').replace("\n", '').replace("\r", '')
    _tmp, blank, stringMode = '', False, False
    for _c in code :
        if _c == ' ' and not stringMode:
            if not blank: blank = True
        else:
            if blank and not stringMode: _tmp += ' '*remainingBlankCount; blank = False
            _tmp += _c
        if _c == '"' or _c == '\'': 
            if not stringMode: stringMode = _c
            else: stringMode = False
    if stringMode: print("SyntaxError: incomplete input of string"); exit(1)

    return _tmp


def tupleParsing(parameterCode:str) -> list:
    # Handling an array of function parameters
    if parameterCode == '': return []

    elementArray, element, stringMode, parenthesisLevel = [], '', False, 0
    for _i in range(len(parameterCode)):
        if parameterCode[_i] == '"' or parameterCode[_i] == '\'':
            if stringMode and parameterCode[_i] == stringMode: stringMode = False
            else: stringMode = parameterCode[_i]
        if not stringMode:
            if parameterCode[_i] == '(': parenthesisLevel += 1
            elif parameterCode[_i] == ')':
                if parenthesisLevel == 0: print("SyntaxError: Cannot match closing parenthesis ')'"); exit(1)
                else: parenthesisLevel -= 1
        if not stringMode and not parenthesisLevel and parameterCode[_i] == ',': 
            elementArray.append(element)
            element = ''
        else: element += parameterCode[_i]
    elementArray.append(element)

    return elementArray

def stringCodeRestoration(code:str, stringCodeTable:dict):
    for _i in stringCodeTable.keys():
        code = code.replace(f"${_i}", stringCodeTable[_i])
    return code

def getStringCode(code:str) -> tuple: 
    index, _stringMode, mainCode, _stringCode, stringCodeTable, _count = 0, False,  '', '', {}, 0
    while index < len(code):
        if code[index] == '"' or code[index] == '\'': 
            if not _stringMode: _stringMode = code[index]; _count += 1
            elif _stringMode == code[index]: 
                _stringMode = False
                while f"${_count}" in code: _count += 1
                stringCodeTable[_count] = _stringCode+code[index]; _stringCode = ''; mainCode += f"${_count}"
                index += 1; continue
        
        if _stringMode: _stringCode += code[index]
        else: mainCode += code[index]
        index += 1
    if _stringMode: print("SyntaxError: incomplete input of string"); exit(1)

    return mainCode, stringCodeTable


def createVariable(variablePool:dict, currentScope:str, variableName:str, variableType:str, internal) -> list:
    currentScopeArray = currentScope.split('.')
    accessWidth = len(currentScopeArray)
    _tmp = variablePool
    for _l in range(accessWidth):
        _tmp = _tmp[currentScopeArray[_l]]["variablePool"]

    _tmp[variableName] = {"type": variableType, "internal": internal, "variablePool": {}}

    return _tmp[variableName]

def getValue(variablePool:dict, currentScope:str, variableName:str):
    currentScopeArray = currentScope.split('.')
    accessWidth = len(currentScopeArray)
    variableScopeArray = []
    for _i in range(accessWidth):
        _tmp = variablePool
        for _l in range(accessWidth-_i):
            if currentScopeArray[_l] not in _tmp: continue
            _tmp = _tmp[currentScopeArray[_l]]["variablePool"]
            variableScopeArray.append(currentScopeArray[_l])
        if variableName in _tmp: 
            return _tmp[variableName], '.'.join(variableScopeArray)
        variableScopeArray = []
    
    return None, currentScope


def assignmentSentence(code:str, stringCodeTable:dict, variablePool:dict, currentScope:str):
    _value = singleCommandParsing(stringCodeRestoration(code[code.find('=')+1:len(code)], stringCodeTable), variablePool, currentScope)
    _element = code[0:code.find('=')]
    _operationSymbol = ''
    if code[code.find('=')-1] in ['+', '-', '*', '/', '%']: 
        _element = code[0:code.find('=')-1]; _operationSymbol = code[code.find('=')-1]

    try:
        typeName, variableName = _element.split("::")
    except ValueError:
        if '[' in _element and _element[-1] == ']':
            _variable = getValue(variablePool, currentScope, _element[0:_element.find('[')])[0]
            if not _variable: print(f"NameError: name '{_element[0:_element.find('[')]}' is not defined"); exit(1)

            _type = _variable['type']
            try: _typeName, _capacity = _type[0:_type.find('[')], int(_type[_type.find('[')+1:-1])
            except: print(f"SyntaxError: invalid array operation."); exit(1)
            _index = singleCommandParsing(stringCodeRestoration(_element[_element.find('[')+1:-1], stringCodeTable), variablePool, currentScope)
            if not type(_index) == int: print("TypeError: the type of index value must be 'int'")

            if _typeName != type(_value).__name__ and not (_typeName == "float" and type(_value).__name__ == "int") and \
                type(_value).__name__ != "NoneType": print("TypeError: Cannot assign values to variables of different types.", _value, _element); exit(1)
            
            _length = len(_variable["variablePool"]["__value"])
            if _capacity > _index >= _length-1:
                for _i in range(_index-_length+1): _variable["variablePool"]["__value"].append(None)
                if _operationSymbol == '': _variable["variablePool"]["__value"][_index] = _value
                else:
                    _value = singleCommandParsing(f"{_element}{_operationSymbol}{_value}", variablePool, currentScope)
                    _variable["variablePool"]["__value"][_index] = _value
                return _value
            elif _index < _length-1:
                if _operationSymbol == '': _variable["variablePool"]["__value"][_index] = _value
                else:
                    _value = singleCommandParsing(f"{_element}{_operationSymbol}{_value}", variablePool, currentScope)
                    _variable["variablePool"]["__value"][_index] = _value
                return _value
            else: print(f"SyntaxError: invalid array operation."); exit(1)
        
        variableValue = getValue(variablePool, currentScope, stringCodeRestoration(_element, stringCodeTable))[0]
        if not variableValue: print("SyntaxError: Type definition required"); exit(1)
        if _operationSymbol == '': variableValue["variablePool"]["__value"] = _value
        else:
            _value = singleCommandParsing(f"{_element}{_operationSymbol}{_value}", variablePool, currentScope)
            variableValue["variablePool"]["__value"] = _value

        return _value

    # Invalid symbol or invalid variable name
    for _i in ["while", "function", "str", "int", "float", "if", "else", "return", "break", "continue"]:
        if variableName == _i: print("SyntaxError: invalid syntax"); exit(1)
    for _i in invalidSymbol:
        if _i in variableName: print("SyntaxError: invalid syntax"); exit(1)
    if '[' in typeName and typeName[-1] == ']':
        typeName, index = typeName[0:typeName.find('[')], singleCommandParsing(stringCodeRestoration(typeName[typeName.find('[')+1:-1], stringCodeTable), variablePool, currentScope)
        if not type(index) == int: print("TypeError: the type of index value must be 'int'")
        if not type(_value).__name__ == "NoneType":
            if len(_value) > index: print("IndexError: The actual element quality cannot exceed the array index"); exit(1)
            if not len(_value) == 0:
                if type(_value[0]).__name__ != typeName and not (type(_value[0]).__name__ == "int" and typeName == "float"):
                    print("TypeError: Cannot assign values to variables of different types."); exit(1)
        createVariable(variablePool, currentScope, variableName, typeName+f"[{index}]", None)["variablePool"]["__value"] = _value
    elif typeName == type(_value).__name__ or type(_value).__name__=="NoneType" or \
        (typeName == "float" and type(_value).__name__ == "int"):
        if _operationSymbol == '': 
            createVariable(variablePool, currentScope, variableName, typeName, None)["variablePool"]["__value"] = _value
        else:
            singleCommandParsing(f"{variableName}={variableName}{_operationSymbol}{_value}", variablePool, currentScope)
    else:
        print("TypeError: Cannot assign values to variables of different types"); exit(1)

    return _value

def functionCall(code:str, stringCodeTable:dict, variablePool:dict, currentScope:str):
    functionName = stringCodeRestoration(code[0:code.find('(')], stringCodeTable) # function name obtained from the code

    functionInformation, functionScope = getValue(variablePool, currentScope, functionName)
    if not functionInformation: print(f"NameError: name '{functionName}' is not defined"); exit(1)
    if not functionInformation["type"] == "function": 
        print(f"TypeError: '{functionInformation['type']}' object is not callable"); exit(1)
       
    originFunctionVariablePool = deepcopy(functionInformation["variablePool"])

    parameterCode = stringCodeRestoration(code[code.find('(')+1:-1], stringCodeTable)
    elementArray = tupleParsing(parameterCode)

    _valueArray = []
    for _i in elementArray: _valueArray.append(singleCommandParsing(_i, variablePool, currentScope))   
    
    returnValueType = functionInformation["variablePool"]["__returnValueType"]
    functionParameterArray = functionInformation["variablePool"]["__parameterList"]
    if len(_valueArray) < len(functionParameterArray): 
        print(f"TypeError: {functionName}() missing {len(functionParameterArray)-len(_valueArray)} required argument"); exit(1)
    elif len(_valueArray) > len(functionParameterArray): 
        print(f"TypeError: Only {len(_valueArray)-len(functionParameterArray)} parameters are required for {functionName}() "); exit(3)
    for _i in range(len(_valueArray)):
        _valueType = type(_valueArray[_i]).__name__
        _parameterType = functionInformation["variablePool"][functionParameterArray[_i]]["type"]
        
        if not ((_parameterType ==_valueType and '[' not in _parameterType) and _valueType == "NoneType" and \
                (_parameterType == "float" and _valueType == "int")):
            if '[' in _parameterType and ']' in _parameterType[-1]:
                _typeName = _parameterType[0:_parameterType.find('[')]
                if type(_valueArray[_i][0]).__name__ != _typeName and not (type(_valueArray[_i][0]).__name__ == "int" and _typeName == "float"):
                    print("TypeError: The return value defined by the function does not match the actual return value"); exit(1)
                try: _length = int(_parameterType[_parameterType.find('[')+1:-1])
                except: print(f"SyntaxError: invalid array operation."); exit(1)
                if not _length <= len(_valueArray[_i]): print(f"SyntaxError: invalid array operation."); exit(1)
        else: print("TypeError: The formal and actual parameter types must be consistent", _parameterType, _valueType); exit(1)

        functionInformation["variablePool"][functionParameterArray[_i]]["variablePool"]["__value"] = _valueArray[_i]
    
    if functionInformation["internal"]:
        try:
            _value = functionInformation["internal"](variablePool, functionScope+f".{functionName}")
        except: print("RuntimeError: faulty internal function functionality"); exit(1)
    else:
        try: _value = run(functionInformation["variablePool"]["__code"], True, False, variablePool, functionScope+f".{functionName}")[0]
        except RecursionError: print("RuntimeError: Exceeding maximum recursion depth: 1024"); exit(1)
    functionInformation["variablePool"] = originFunctionVariablePool

    if (returnValueType == type(_value).__name__ and '[' not in returnValueType) or type(_value).__name__ == "NoneType" or \
        (returnValueType == "float" and type(_value).__name__ == "int"): return _value
    else:
        if '[' in returnValueType and ']' in returnValueType[-1]:
            _typeName = returnValueType[0:returnValueType.find('[')]
            if type(_value[0]).__name__ != _typeName and not (type(_value[0]).__name__ == "int" and _typeName == "float"):
                print("TypeError: The return value defined by the function does not match the actual return value"); exit(1)
            try: _length = int(returnValueType[returnValueType.find('[')+1:-1])
            except: print(f"SyntaxError: invalid array operation."); exit(1)
            if _length <= len(_value): return _value
            else: print(f"SyntaxError: invalid array operation."); exit(1)
        print("TypeError: The return value defined by the function does not match the actual return value"); exit(1)

def operationSentence(code:str, stringCodeTable:dict, variablePool:dict, currentScope:str): 
    # Divide symbols into different groups
    # Different groups represent different priorities
    # The higher the priority of the group, the higher the priority
    symbolArray = [["||", "&&", '!'], ["==", ">=", "<=", '>', '<'], ['+', '-', '*', '/', '%']]

    # Divide the sentence into multiple blocks based on symbols
    if code[0] == '(' and code[-1] == ')': code = code[1:-1]

    sentence = stringCodeRestoration(code[0:len(code)], stringCodeTable)
    element, stringMode, parenthesisLevel, bracketLevel, whetherAddingElement, elementArray = '', False, 0, 0, False, []
    for _group in symbolArray:
        _groupBeLocked, _i = False, 0
        while _i < len(sentence):
            if sentence[_i] == '"' or sentence[_i] == '\'': 
                if not stringMode: stringMode = sentence[_i]
                elif stringMode == sentence[_i]: stringMode = False
            
            if not stringMode:
                if sentence[_i] == '(': parenthesisLevel += 1
                elif sentence[_i] == ')':
                    if parenthesisLevel == 0: print("SyntaxError: Cannot match closing parenthesis ')'"); exit(1)
                    else: parenthesisLevel -= 1
                if sentence[_i] == '[': bracketLevel += 1
                elif sentence[_i] == ']':
                    if bracketLevel == 0: print("SyntaxError: Cannot match closing parenthesis ')'"); exit(1)
                    else: bracketLevel -= 1
                if parenthesisLevel == 0 and bracketLevel == 0:
                    for _symbol in _group:
                        if not sentence[_i] == _symbol[0]: continue
                        for _l in range(len(_symbol)): 
                            if sentence[_i+_l] != _symbol[_l]: break
                        else:
                            elementArray.extend([element, _symbol])
                            _groupBeLocked, whetherAddingElement, element = True, True, ''
                            _i += len(_symbol)
                            break
            if not whetherAddingElement: element += sentence[_i]; _i += 1
            else: whetherAddingElement = False
        if _groupBeLocked == True: break
        element = '' # Clear the legacy value of the previous group
    else: element = sentence
    if stringMode: print("SyntaxError: incomplete input of string"); exit(1)
    elif parenthesisLevel: print("SyntaxError: Cannot match opening parenthesis '('"); exit(1)
    elementArray.append(element)

    if '' in elementArray: 
        _i, _tmp = 0, []
        while _i < len(elementArray):
            if elementArray[_i] == '' and elementArray[_i+1] == '-':
                _tmp.append(elementArray[_i+1]+elementArray[_i+2])
                _i += 3; continue
            elif elementArray[_i] == '' and elementArray[_i+1] == '!':
                _tmp.append(elementArray[_i+1])
                _i += 2; continue
            _tmp.append(elementArray[_i])
            _i += 1
        if '' in _tmp: print("SyntaxError: invalid syntax"); exit(1)
        elementArray = _tmp

    # Perform arithmetic operations
    elementParsing = lambda element: singleCommandParsing(element, variablePool, currentScope)
    symbolArray = ["||", "&&", "==", ">=", "<=", '>', '<', '+', '-', '*', '/', '%']
    if elementArray[0] in symbolArray: print("SyntaxError: invalid syntax"); exit(1)
    elif elementArray[0] == '!':
        if elementArray[0] in symbolArray: print("SyntaxError: invalid syntax"); exit(1)
        _value = None
    else:
        _value = elementParsing(elementArray[0])
    symbolArray.append('!')
    for _i in range(len(elementArray)):
        if elementArray[_i] in symbolArray:
            try:
                if elementArray[_i+1] in symbolArray: print("SyntaxError: invalid syntax"); exit(1)

                _anotherValue = elementParsing(elementArray[_i+1])
                if elementArray[_i] == "||": _value = int(_value or _anotherValue)
                elif elementArray[_i] == "&&": _value = int(_value and _anotherValue)
                elif elementArray[_i] == '!': _value = int(not _anotherValue)
                elif elementArray[_i] == "==": _value = int(_value == _anotherValue)
                elif elementArray[_i] == ">=": _value = int(_value >= _anotherValue)
                elif elementArray[_i] == "<=": _value = int(_value <= _anotherValue)
                elif elementArray[_i] == '>': _value = int(_value > _anotherValue)
                elif elementArray[_i] == '<': _value = int(_value < _anotherValue)
                elif elementArray[_i] == '+': _value = _value + _anotherValue
                elif elementArray[_i] == '-': _value = _value - _anotherValue
                elif elementArray[_i] == '*': _value = _value * _anotherValue
                elif elementArray[_i] == '/': _value = _value / _anotherValue
                elif elementArray[_i] == '%': _value = _value % _anotherValue
            except IndexError: print("SyntaxError: invalid syntax"); exit(1)
            except TypeError: 
                print(element, elementArray, _value)
                print("TypeError: Different types of values cannot be operated on directly")
                if type(_value).__name__ == "NoneType" or type(_anotherValue).__name__ == "NoneType":
                    print(" └─ Warning: type `null` cannot be operated on with any type", f"`{_value}`", f"`{_anotherValue}`")
                exit(1)
    return _value

def singleCommandParsing(code:str, variablePool:dict, currentScope:str):
    code = deleteBlankPart(code, 0)
    symbolTable = ['=', '>', '<', '!', '(', '+', '-', '*', '/', '%', '|', '&']
    
    mainCode, stringCodeTable = getStringCode(code)

    # assignment
    if '=' in mainCode and mainCode[mainCode.find('=')+1] != '=' and mainCode[mainCode.find('=')-1] not in ['>', '<']:
        return assignmentSentence(mainCode, stringCodeTable, variablePool, currentScope)
    
    # function call
    if mainCode[0] != '(' and '(' in mainCode and mainCode[-1] == ')':
        for _i in symbolTable:
            if _i in mainCode[0:mainCode.find('(')]: break
        else:
            return functionCall(mainCode, stringCodeTable, variablePool, currentScope)
    
    # array operation
    if mainCode[0] != '[' and '[' in mainCode and mainCode[-1] == ']':
        for _i in symbolTable:
            if _i in mainCode[0:mainCode.find('[')]: break
        else:
            _variable = getValue(variablePool, currentScope, mainCode[0:mainCode.find('[')])[0]
            if not _variable: print(f"NameError: name '{mainCode[0:mainCode.find('[')]}' is not defined"); exit(1)
            _index = singleCommandParsing(stringCodeRestoration(mainCode[mainCode.find('[')+1:-1], stringCodeTable), variablePool, currentScope)
            if not type(_index) == int: print("TypeError: the type of index value must be 'int'")
            try:
                _value = _variable["variablePool"]["__value"]
                return _variable["variablePool"]["__value"][_index]
            except: print(f"SyntaxError: invalid array operation."); exit(1)

    # judgment (operation)
    for _i in symbolTable: 
        if _i in mainCode: 
            if mainCode.count('-'):
                # negative number 
                try: 
                    _tmp = stringCodeRestoration(mainCode, stringCodeTable)
                    if int(_tmp) == float(_tmp): return int(_tmp)
                    return float(_tmp)
                except: ...
            return operationSentence(mainCode, stringCodeTable, variablePool, currentScope)

    # Obtain value normally, whether it is in variable pool
    _value = getValue(variablePool, currentScope, stringCodeRestoration(mainCode, stringCodeTable))[0]
    if _value != None: return _value['variablePool']["__value"]
    # whether it is a regular value, such as int, float etc.
    if mainCode == "null": return None
    if (code[0] == '"' or code[0] == '\'') and code[-1] == code[0]: 
        # it is a string
        return code[1:-1].replace("\\t", '\t').replace("\\n", '\n').replace("\\r", '\r')
    elif mainCode[0] == '[' and mainCode[-1] == ']': 
        # it is an array, and it will create an array
        _tmp, elementArray = '', []
        for _i in range(1, len(mainCode)-1): 
            if mainCode[_i] == ',': elementArray.append(_tmp); _tmp = ''; continue
            _tmp += mainCode[_i]
        if _tmp != '': elementArray.append(_tmp)

        elementType = "NoneType"; _tmp = []
        for _i in elementArray: 
            if elementType == type(_i).__name__ or elementType == "NoneType" or type(_i).__name__ == "NoneType" or \
                (elementType == "float" and type(_i).__name__ == "int"): elementType = type(_i).__name__; 
            else: print(f"TypeError: The types of each element in the array must be consistent"); exit(1)
            _tmp.append(singleCommandParsing(_i, variablePool, currentScope))

        return _tmp
    try:
        if float(code) == int(float(code)): return int(float(code))
        else: return float(code)
    except ValueError: print(f"NameError: name '{code}' is not defined"); exit(1)


def keywordComparison(code:str, index:int, keyword:str) -> int:
    if code[index] == ' ': 
        while True:
            if index == len(code): return None
            if code[index] == ' ': index += 1
            else: break
    
    comparison = ''
    while True:
        if index == len(code): return None
        if code[index] == ' ' or code[index] == '(' or code[index] == ';': break
        comparison += code[index]; index += 1

    if comparison == keyword: return index
    else: return None

def obtainCodeBlock(code:str, index:int, symbol:tuple) -> tuple:
    # Obtain code block, 
    # for example, code blocks enclosed in parentheses or braces and single line commands

    # Delete the bloank
    # print(code, index)
    try:
        if code[index] == ' ': index += 1
    except IndexError: print("SyntaxError: incomplete input"); exit(1)
    # Obrain code block
    if not len(symbol) == 0:
        if not code[index] == symbol[0]: print("SyntaxError: invalid syntax"); exit(1)
        else: index += 1
        codeBlock, _stringMode, parenthesisLevel = '', False, 1
        while index < len(code): 
            if code[index] == '"' or code[index] == '\'': 
                if not _stringMode: _stringMode = code[index]
                elif _stringMode == code[index]: _stringMode = False
            if not _stringMode:
                if code[index] == symbol[0]: parenthesisLevel += 1
                elif code[index] == symbol[1]:
                    if parenthesisLevel == 0: print("SyntaxError: Cannot match closing parenthesis ')'"); exit(1)
                    else: parenthesisLevel -= 1    
            if code[index] == symbol[1] and not _stringMode and not parenthesisLevel: break        
            codeBlock += code[index]; index += 1
        else: print("SyntaxError: invalid syntax"); exit(1)
        index += 1 

        return codeBlock, index
    
    endSymbol, codeBlock, _stringMode, parenthesisLevel = 0, '', False, 0
    while index < len(code):
        if code[index] == '"' or code[index] == '\'': 
            if not _stringMode: _stringMode = code[index]
            elif _stringMode == code[index]: _stringMode = False
        if not endSymbol: 
            if code[index] == '{': endSymbol = 1
        if not _stringMode:
            if endSymbol and code[index] == '{': parenthesisLevel += 1
            elif endSymbol and code[index] == '}':
                if parenthesisLevel == 0: print("SyntaxError: Cannot match closing parenthesis '}'"); exit(1)
                else: parenthesisLevel -= 1 
            if not endSymbol and code[index] == ';': codeBlock += code[index]; break
            if endSymbol and code[index] == '}' and not parenthesisLevel: codeBlock += code[index]; break
        codeBlock += code[index]; index += 1
    else: print("SyntaxError: invalid syntax"); exit(1)
    index += 1

    if codeBlock[0] == '{' and codeBlock[-1] == '}':  codeBlock = codeBlock[1:-1]

    return codeBlock, index

def run(code:str, inFunction:bool, inLoop:bool, variablePool:dict, currentScope:str):
    keywordArray = ["if", "else", "while", "break", "continue", "function", "return", "import"]

    index, result, elseJudgement, outOfLoop = 0, None, False, 0
    
    while index < len(code):
        # Find keywords that match the requirements
        keyword = None
        comparsionResult = None
        for _k in keywordArray:
            comparsionResult = keywordComparison(code, index, _k)
            if comparsionResult: keyword = _k; break

        # No keywords match
        if keyword == None: 
            # Read a single element
            element, stringMode = '', False
            while index < len(code):
                if code[index] == '"' or code[index] == '\'': 
                    if not stringMode: stringMode = code[index]
                    else: stringMode = False
                if code[index] == ';' and not stringMode: break
                element += code[index]
                index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)

            _result = singleCommandParsing(element, variablePool, currentScope)
            index += 1; continue
        
        index = comparsionResult
        if keyword == "if":
            conditionCode, index = obtainCodeBlock(code, index, ('(', ')'))
            runningCode, index = obtainCodeBlock(code, index, ())

            _condition = singleCommandParsing(conditionCode, variablePool, currentScope)
            if _condition: 
                _result, _elseJudgement, _inLoop, _outOfLoop = run(deleteBlankPart(runningCode, 1), inFunction, inLoop, variablePool, currentScope)
                if _outOfLoop: outOfLoop = _outOfLoop; break
                if _result: result = _result; break
            else: 
                elseJudgement = True

        elif keyword == "else":
            runningCode, index = obtainCodeBlock(code, index, ())
            if elseJudgement == True: 
                _result, elseJudgement, _inLoop, _outOfLoop = run(deleteBlankPart(runningCode, 1), inFunction, inLoop, variablePool, currentScope)
                if _outOfLoop: outOfLoop = _outOfLoop; break
                if _result: result = _result; break

        elif keyword == "while":
            elseJudgement = False
            conditionCode, index = obtainCodeBlock(code, index, ('(', ')'))
            runningCode, index = obtainCodeBlock(code, index, ())
            
            _result = None
            while singleCommandParsing(conditionCode, variablePool, currentScope):
                _result, elseJudgement, _inLoop, _outOfLoop = run(deleteBlankPart(runningCode, 1), inFunction, True, variablePool, currentScope)
                if _result or _outOfLoop == 1: break
            if _result: result = _result; break

        elif keyword == "break":
            if not inLoop: print("SyntaxError: 'break' outside loop"); exit(1)
            if code[index] == ' ': index += 1 # Delete the blank
            if code[index] == ';': index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)
            outOfLoop = 1; break
        
        elif keyword == "continue":
            if not inLoop: print("SyntaxError: 'break' outside loop"); exit(1)
            if code[index] == ' ': index += 1 # Delete the blank
            if code[index] == ';': index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)
            outOfLoop = 2; break
        
        elif keyword == "function":
            elseJudgement = False
            if code[index] == ' ': index += 1 # Delete the blank
            _element = ''
            while index < len(code):
                if code[index] == '(': break
                _element += code[index]
                index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)

            # Initialize function information
            _element, _stringCodeTable = getStringCode(_element)
            _name =  _element.split("::")[1]
            _element += "=null"
        
            assignmentSentence(_element, _stringCodeTable, variablePool, currentScope)

            _variablePool = getValue(variablePool, currentScope, _name)[0]
            del _variablePool["variablePool"]["__value"]
            _variablePool["variablePool"]["__returnValueType"] = _variablePool["type"]
            _variablePool["type"] = "function"
            _variablePool["variablePool"]["__parameterList"] = []

            _parameterCode, index = obtainCodeBlock(code, index, ('(', ')'))
            _parameterCodeTable = tupleParsing(_parameterCode)

            runningCode, index = obtainCodeBlock(code, index, ())
            _variablePool["variablePool"]["__code"] = runningCode

            for _parameterCode in _parameterCodeTable:
                _pCode, _pTable = getStringCode(_parameterCode)
                _pName = _pCode.split("::")[1]
                if not '=' in _pCode: _pCode += "=null"
                _variablePool["variablePool"]["__parameterList"].append(_pName)
                assignmentSentence(deleteBlankPart(_pCode, 0), _pTable, variablePool, currentScope+f".{_name}")

        elif keyword == "return":
            if not inFunction: print("SyntaxError: 'return' outside function"); exit(1)
            elseJudgement = False
            if code[index] == ' ': index += 1 # Delete the blank
            _element, _stringMode = '', False
            while index < len(code): 
                if code[index] == '"' or code[index] == '\'': 
                    if not _stringMode: _stringMode = code[index]
                    elif _stringMode == code[index]: _stringMode = False
                if not _stringMode and code[index] == ';': break
                _element += code[index]
                index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)
            index += 1

            result = singleCommandParsing(_element, variablePool, currentScope); break
        
        elif keyword == "import":
            elseJudgement = False
            if code[index] == ' ': index += 1 # Delete the blank
            _element, _stringMode = '', False
            while index < len(code): 
                if code[index] == '"' or code[index] == '\'': 
                    if not _stringMode: _stringMode = code[index]
                    elif _stringMode == code[index]: _stringMode = False
                if not _stringMode and code[index] == ';': break
                _element += code[index]
                index += 1
            else: print("SyntaxError: invalid syntax"); exit(1)
            index += 1
            
            from os import listdir
            for _f in listdir(currentLibraryPath):
                if _f == f"{_element}.cl":  
                    run(getSourceCode(currentLibraryPath+f"{_element}.cl"), False, False, variablePool, "<runtime>")
                    break
            else: run(getSourceCode(currentRuntimePath+f"{_element}.cl"), False, False, variablePool, "<runtime>")

    return result, elseJudgement, inLoop, outOfLoop
