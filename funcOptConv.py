#when hit a function, parse, append parsed back to code, but in order.
import re
import sys
global numthreads
numthreads=8
#rewrite tailreturn
def getAnArg (args):
    stack=""
    splitPoint=-1
    for i in range(len(args)):
        if(args[i]==","and stack==""):
            return (args[:i],args[i+1:])
        if(args[i]=='['):
            stack+="]"
        if(args[i]=='('):
            stack+=")"
        if(args[i]=='{'):
            stack+="}"
        if(args[i]==stack[:-1]):
            stack=stack[:-1]
    if(stack!=""):
        #print(stack)
        return None
    return (args,"")
            
def decomposeCall(line):
    line=line.strip()
    name=line[:line.index("(")]
    posarg=""
    namearg=""
    args=line[line.index("(")+1:line.rindex(")")]
    #print(args)
    args=args.strip()
    firstArg=""
    while(args!=""):
        #print(getAnArg(args))
        firstArg,args=getAnArg(args)
        args=args.strip()
        firstArg=firstArg.strip()
        nameArgFlag=re.compile(r"^[^\d\W]\w*=.*")
        if(nameArgFlag.match(firstArg)):
            namearg+=firstArg.replace("=",":",1)+","
        else:
            posarg+=firstArg+","
    if(posarg!=""):
        posarg=posarg[:-1]
    if(namearg!=""):
        namearg=namearg[:-1]
    nuLine="["+name+","+"["+posarg+"],{"+namearg+"}]"
    return nuLine
#print(decomposeCall(" doAThing(arg1, 2+7, foobar=3)"))
file=open(sys.argv[1],"r")
outFile=open(sys.argv[2],"w")
inparallel=False
whitespace=""
parallelCall="=parallelize(["
nameArgFlag=re.compile(r"^[^\d\W]\w*=.*")
for line in file:
    if(line.strip().startswith("parallel:")):
        whitespace=line[:line.index("parallel:")]
        if('\t' in whitespace):
            whitespace+="\t"
        else:
            whitespace+="    "
        inparallel=True
        continue
    if(inparallel):
        if(not (line.startswith(whitespace) or line.strip().startswith("#"))):
            inparallel=False
            outFile.write(parallelCall[:-1]+"],"+str(numthreads)+")\n")
            line=""
            parallelCall="=parallelize(["
        else:
            if(nameArgFlag.match(line.strip())):
                
                parallelCall+=decomposeCall(line[line.index('=')+1:])+","
                parallelCall=line[:line.index('=')]+","+parallelCall
            else:
                parallelCall+=decomposeCall(line)+","
                parallelCall="NOTAVARIABLE,"+parallelCall
    if(line.strip().startswith("tailreturn ")):
        whitespace=line[:line.index("tailreturn ")]
        call = line[line.index("tailreturn ")+len("tailreturn "):]
        line=whitespace+"return [[\"tail\",tail],"+decomposeCall(call)+"]"
    if(not inparallel):
        outFile.write(line)
outFile.close()