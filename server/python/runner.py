from language import *

result,errors=run("Test.txt","StartCycle i=1:10:2{\n\tPrint(i)\n}")

if errors:
    errors.show_error()
elif result:
    print(result)