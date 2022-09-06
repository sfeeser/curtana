#!/usr/bin/env python3
import time
import os
from subprocess import call
import yaml
import crayons

def clear():
    # check and make call for specific operating system
    _ = call('clear' if os.name =='posix' else 'cls')

def commandcount(commands):
  i = 0
  for command in commands:
      i += 1
  return i

def studentcheck():
    print("tst")
    with open("student.log", "r") as logfile:
        commands = logfile.readlines()
    clear()
    print(commands)
    #print title in bold green
    print(crayons.green(f"There are {commandcount(commands)} lines")
    # farm will be equal to one of the dict within the list "farms"
    for command in commands:
        #print name of the farms in bold yellow
        print(crayons.yellow(f"{command} ", bold=True))

def main():
    try:
        while True:
            studentcheck()
            time.sleep(2)
    except KeyboardInterrupt:
        pass


main()
