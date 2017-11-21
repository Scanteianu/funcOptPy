#nohup name > textFile &
#to check if dead ps -la or top
from functools import wraps
import json
import time
global dynamicTable
from multiprocessing import Process, Queue
dynamicTable={}
def dynamic(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        global dynamicTable
        key=str(func)+"~"+json.dumps(args)+"~"+json.dumps(kwargs)
        if(key not in dynamicTable):
            result = func(*args, **kwargs)
            dynamicTable[key]=result
        return dynamicTable[key]
    return wrapper
def tailCall(tailfunc):
    @wraps(tailfunc)
    def tailwrapper(*args, **kwargs):
        result = tailfunc(*args, **kwargs)
        while(True):
            
            try:
                if(result[0][0]=="tail" and not result[0][1]):
                    '''print "~~~~~here"
                    print args
                    print kwargs
                    tailFlag=False
                    if("tail" in kwargs):
                        tailFlag=True'''
                    tail = result[0][1]
                    othertailfunc=result[1]
                    args=result[2]
                    kwargs=result[3]
                    '''if(tailFlag):
                        kwargs["tail"]=True
                    else:
                        kwargs["tail"]=False'''
                    kwargs["tail"]=True
                    result=othertailfunc(*args,**kwargs)
                    result[0][1]=False
                else:
                    #print "recursion depth"
                    return result
            except TypeError, e:
                #print(e)
                #print("no loop, man")
                return result
    return tailwrapper       
#@dynamic
def fib(i):
    if(i<2):
        return 1
    return fib(i-1)+fib(i-2)
    
def runinthread(queue, ansQueue):
    #global funcList
    #global counter
    
    #print("started"+str(indexNum))
    while(not queue.empty()):
        func=queue.get()
        ansQueue.put((func[0][0](*func[0][1], **func[0][2]),func[1]))
        #print("did "+str(func[1]))
    return 0
#call with a list of tuples (func, args, kwargs), get a list of result objects in the same order.
def parallelize(myfunclist, numThreads):
    queue = Queue()
    ansQueue= Queue()
    i=0
    for func in myfunclist:
        queue.put((func, i))
        i+=1
    threadList=[]
    
    totaList=[]

    totaList = range(len(myfunclist))
    
    counter=0
    for i in range(numThreads):
        thread = Process(target = runinthread, args = (queue,ansQueue))
        thread.start()
        threadList.append(thread)
    for thread in threadList:
        #print("join")
        thread.join()
    while(not ansQueue.empty()):
        func=ansQueue.get()
        totaList[func[1]]=func[0]
    return totaList
#to make tailreturn: annotate with tailCall;
#then, for tail call, return list [["tail",tail], func, args, kwargs]
#must have kwarg tail=False in header.
#for normal return, proceed as standard.
'''
@tailCall
def tailPrint(i, tail=False):
    if(i==0):
        return 1
    if(i%1000==0):
        print i
    return [["tail",tail], tailPrint, [i-1],{}]# tailPrint(i-1)
def noTailPrint(i, tail=False):
    if(i==0):
        return 1
    if(i%1000==0):
        print i
    return noTailPrint(i-1)

@tailCall
def factorial(n, mult, tail=False):
    if(n==1):
        return mult
    return [["tail",tail],factorial, [n-1,mult*n],{}]
#print(fib(200))

startTime=time.time()
print("start non-parallel")
for i in range(16):
    print(fib(32))
print("end non-parallel")
print(time.time()-startTime)
startTime=time.time()
print("start parallel")
#parallelArg
parallelArg = []
for i in range(16):
    parallelArg.append((fib, (32,), {}))
result=parallelize(parallelArg,16)
for i in result:
    print(i)
print("end parallel")
print(time.time()-startTime)

#print(tailPrint(20000))
#print(factorial(50,1))
#print(noTailPrint(20000))
'''