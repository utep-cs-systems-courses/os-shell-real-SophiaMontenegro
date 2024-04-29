#!/usr/bin/env python3
import os, sys, re

# what does dup2() do?


def cdCommand(command):
    #Change directories
    if len(command) >= 2:
        try:
            os.chdir(command[1])
        except FileNotFoundError:
            os.write(2, f"bash: cd {command[1]}: No such file or directory\mn".encode())
    else:
       os.chdir(os.environ['HOME'])

def redirection(command): # can there be a redirection of both??
    #redirection of input
    if '<' in command:
        index = command.index('<')
        inputFile = command.pop(index + 1) # get the input file
        os.close(0) # close input
        os.open(inputfile, os.O_RDONLY)
        os.set_inheritable(1, True)
        return True
        
    elif '>' in command: # redirection of output
        index = command.index('>')
        outputFile = command.pop(index + 1)
        os.close(1) # close output
        os.open(outputFile, os.O_CREAT | os.O_WRONLY)
        os.set_inheritable(0, True)
        return True

    os.write(2, "Invalid redirection\n".encode())
    return False

def run(command):
    # try to run a given command
    try:
        os.execve(command[0], command, os.environ)
    except FileNotFoundError:
        pass

    for directory in re.split(':', os.environ['PATH']):
        program = f"{directory}/{command[0]}"
        try:
            os.execve(program, command, os.environ)
        except FileNotFoundError:
            pass
    os.write(2, f"{command[0]}: Command not found\n".encode())
    sys.exit(1)

def pipes(command):
    # pipes (looked at forkPipeDemo.c)
    reader, writer = os.pipe()
    index = command.index('|')
    
    pid = os.fork()
    
    if pid < 0: # failed
        sys.exit(1) 

    elif pid == 0: # child
        os.close(1) # close out
        os.dup(writer) # duplicate writer to out
        os.set_inheritable(1, True)
        os.close(reader)
        os.close(writer)
        run(command[:index])
        
    else: # parent
       os.close(0) #close in
       os.dup(reader) # duplicate reader to in
       os.set_inheritable(0, True)
       os.close(reader)
       os.close(writer)
       run(command[index + 1:])

#def resetRedirection():
    # reset if there was a redirection





#-----------------------------------------------------------------------------    
def shell():
    while True:
        prompt = os.getenv('PS1', '$')
        #print(prompt)

        command = input(prompt).strip()
        command = list(filter(None, command.split(' ')))
        
        if len(command) == 0: #nothing
            print()
            continue

        elif command[0] == 'exit':
            sys.exit(0) #exit out of shell
            
        elif command[0] == 'cd':
            #change directory
            cdCommand(command)
            continue
        
        pid = os.fork()# create child process
        wait = True
        redirect = False

        if command[-1] == '&': # run in the background
            wait = False
            command.pop()

        if pid == -1: # no child process was created
             os.write(2, f"Process creation failed\n".encode())
             sys.exit(1) # exit
             
        elif pid == 0: # is child
            if '|' in command: # pipe needed
                pipes(command)
                
            elif '<' in command or '>' in command: #redirection input / output
                redirect = redirection(command)#can be true or false
                if not redirect:
                    continue
            
            run(command)
            
        else: # is parent
            if wait:
                os.wait() # wait for child
            
            
        
        #else:
            #print("command is not found")

if __name__ == "__main__":
    shell() #runs shell
        
