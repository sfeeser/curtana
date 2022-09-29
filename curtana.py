import time
import os
from subprocess import call
import json
import crayons
import re
from datetime import datetime

def parse(data: str) -> {}:

    """
    Command parsing function
    ----------------------------
    Given a log entry like this:
     "Sep  1 16:06:44 bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a student: student@bchd:/home/student$ sudo apt install python3-pip -y [0]"
  
    Return a command_anatomy of dictinataries like this:
      {     "month": "Sep",day": 1,
            "hours": 16,
            minutes: 10,
            seconds: 44,
           "domain": "bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a",
             "user": "student", 
           "prompt": "student@bchd:/home/student$",
           "command: "sudo apt install python3-pip -y",
           "result": "[0]",
      }

    Parameters:

        data:        (string)  text data to parse
        raw:         (boolean) unprocessed output if True
        quiet:       (boolean) suppress warning messages if True
    """

    

    # REGEX was tested here: https://regex101.com/r/6eO469/1
    command_parser = re.compile(r'''

        (?#regexp & naming based on RFC5424)
        ^(?P<month>[a-zA-Z]{3})\s*
        (?P<day>\d|[012]\d|3[01])\s*
        (?P<hour>[01]\d|2[0-4]):
        (?P<minute>[0-5]\d):
        (?P<second>[0-5]\d)\s*
        (?P<domain>[a-z\.0-9\-]*)\s*
        (?P<user>[a-z]*):?\s
        (?P<prompt>[\/a-zA-Z\.0-9\-@:]*)[\$#]?\s*
        (?P<command>.*)[\$#]?\s*\[
        (?P<result>\d+)\]\s*
        ''', re.VERBOSE
    )

    for line in filter(None, data.splitlines()):
        command_parser_match = command_parser.match(line)
        if command_parser_match:
            command_anatomy = command_parser_match.groupdict()  #re function that Returns dicts, keyed by the subgroup name.
        else:
            command_anatomy= {
                'unparsable': line
            }
    return command_anatomy 



def name_parse(data: str) -> {}:
    name_parser = re.compile(r'''
        ^(?P<prefix>\s*git\s*config\s*--global\s*user\.name)\s*
        "(?P<name>.*)"
        ''', re.VERBOSE
    )
    name_parser_match = name_parser.match(data)
    if name_parser_match:
        name_hints = name_parser_match.groupdict()  #re function that Returns dicts, keyed by the subgroup name.
    else:
        name_hints = {
        'unparsable': data
        }
    return name_hints

"""
Data per 
- studentracker:
    domain: value
    student_name: 
    cmd_peg_count:
    success_peg_count
    fail_peg_count
    time_since_last_
    inactivity_seconds: int
    most_recent_command: string
    commands:
      - command: string
        result: int
        think_time: seconds


"""


def thinktime(start_time):
    # start time

    # convert time string to datetime
    t1 = datetime.strptime(start_time, "%Y:%b:%d:%H:%M:%S")

    # get difference
    delta = datetime.utcnow() - t1
    return delta.total_seconds()



'''
this_command_time = "2022:Sep:22:18:14:22"

# time difference in seconds
sluggy = int(thinktime(this_command_time))

print(f"Time difference is {sluggy} seconds")
print(datetime.utcnow())
'''


student_tracker = {}
student_tracker_list = []
verbose = False


with open("/var/log/students.log", "r") as logfile:
    commands = logfile.readlines()
    for command in commands:
        if verbose:
           print(crayons.green(command,parse(command)), end = '' )
        this_command = parse(command)
        if verbose:
            print(this_command,"\n")
        # The next line is a generator, it will return the idex of an existing student record, else "Init_me"
        index = next((i for i, item in enumerate(student_tracker_list) if item["domain"] == this_command.get('domain')), "Init_me")
        if verbose:
            print(crayons.yellow(student_tracker))
            print(student_tracker_list)
        if index == "Init_me":
           student_tracker = {}
           student_tracker["domain"] = this_command.get('domain')
           student_tracker["student_name"] = ""
           student_tracker["latest_command"]= this_command.get('command')
           student_tracker["cmd_peg_count"] = 1
           if this_command.get("result") == "0":
              student_tracker["success_peg_count"] = 1
              student_tracker["fail_peg_count"] = 0
           else:
              student_tracker["success_peg_count"] = 0
              student_tracker["fail_peg_count"] = 1
           name_check = name_parse(this_command.get("command"))
           student_tracker["student_name"] = name_check.get("name")
           if verbose:
               print(crayons.yellow(student_tracker))
           student_tracker_list.append(student_tracker)
           # student_tracker["commands"] = []
           # + = [["command"] = command.get("command"),  ["time"] = command.get("command"), ["result"] = command.get("result")]
           student_tracker["time_stamp"] = "2022" + ":" + this_command.get('month') + ":" + this_command.get('day') + ":" + this_command.get('hour') + ":" + this_command.get('minute') + ":" + this_command.get('second')

        else:
          student_tracker["latest_command"]= this_command.get('command')
          student_tracker["latest_result"]= this_command.get('result')
          student_tracker_list[index]["cmd_peg_count"] += 1
          if this_command.get("result") == "0":
              student_tracker_list[index]["success_peg_count"] += 1
          else:
              student_tracker_list[index]["fail_peg_count"] += 1
          name_check = name_parse(this_command.get("command"))
          if "name" in name_check:
              student_tracker_list[index]["student_name"] = name_check.get("name")
          student_tracker["time_stamp"] = "2022" + ":" + this_command.get('month') + ":" + this_command.get('day') + ":" + this_command.get('hour') + ":" + this_command.get('minute') + ":" + this_command.get('second')
      
    print(crayons.yellow(f"Time now: {datetime.utcnow()}")) 
    print(crayons.green(f"Student             Cmds   Success  Fail   Time     Results + Latest Command"))
    print(crayons.green(f"------------------  -----  -------  ----   ------   ----------------------------------"))
    for student in student_tracker_list:
        print(crayons.green(f"{str(student.get('student_name')):<17}"), end = '')
        print(crayons.green(f"{student.get('cmd_peg_count'):>8}  "), end = '')
        print(crayons.green(f"{student.get('success_peg_count'):>7}  "), end = '')
        print(crayons.green(f"{student.get('fail_peg_count'):>4}  " ), end = '')
        print(crayons.yellow(f" {student.get('time_stamp')}  "), end = '')
        sluggy = int(thinktime(student.get('time_stamp')))
        print(crayons.yellow(f" {sluggy}  "), end = '')
        if student.get('latest_result') is None:
            print(crayons.green(f"{[  0]}"), end = '' )
        else:
            print(crayons.green(f"[{student.get('latest_result'):>3}]"), end = '' )
            
        print(crayons.green(f" {str(student.get('latest_command')):>3}"))

