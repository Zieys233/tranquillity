# Tranquilly Programming Language
# For learning purposes only
# Author: Benjamin Tang


from sys import argv, exit, setrecursionlimit

def main(argv:list):
    if len(argv) != 2: print("OSError: must have one parameter"); exit(1)

    # Read variablePool file
    from json import loads, JSONDecodeError
    import builtin

    try:
        if '\\' in argv[0]: path = '/'.join(argv[0].split('\\')[:-1])
        elif '/' in argv[0]: path = '/'.join(argv[0].split('/')[:-1])
        else: path = './'

        with open(path+"/Lib/variablePool") as f:
            initalVariablePool = loads(f.read())
            builtin.init(initalVariablePool)
    except FileNotFoundError: print("OSError: Missing orginal varibale pool file"); exit(1)
    except JSONDecodeError: print("OSError: Fatal syntax in original variable pool file"); exit(1)
    
    # Read the source code and run it
    import runtime
    
    if '\\' in argv[0]: runtime.currentRuntimePath = '/'.join(argv[1].split('\\')[:-1])
    elif '/' in argv[0]: runtime.currentRuntimePath = '/'.join(argv[1].split('/')[:-1])
    runtime.currentRuntimePath += '/'
    runtime.currentLibraryPath = path+"/Lib/"

    setrecursionlimit(1024)
    try: runtime.run(runtime.getSourceCode(argv[1]), False, False, initalVariablePool, "<runtime>")
    except KeyboardInterrupt: ...

if __name__ == "__main__":
    main(argv)
