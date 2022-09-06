import time
import os
from subprocess import call
import json
import crayons
import re

def parse(data: str) -> {}:

    """
    Command parsing function
    ----------------------------
    Given a log entry like this:
     "Sep  1 16:06:44 bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a student: student@bchd:/home/student$ sudo apt install python3-pip -y [0]"
  
    Return a command_anatomy of dictinataries like this:
      {     "month": "Sep", 
              "day": 1,
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

student_tracker = {}
student_tracker_list = []

with open("logs", "r") as logfile:
    commands = logfile.readlines()
    for command in commands:
        print(crayons.green(command,parse(command)), end = '' )
        this_command = parse(command)
        print(this_command,"\n")
        index = next((i for i, item in enumerate(student_tracker_list) if item["domain"] == this_command.get('domain')), "Init_me")
        print(crayons.yellow(student_tracker))
        print(type(student_tracker))
        if index == "Init_me":
           student_tracker = {}
           student_tracker["domain"] = this_command.get('domain')
           student_tracker["student_name"] = ""
           student_tracker["cmd_peg_count"] = 1
           if this_command.get("result") == "0":
              student_tracker["success_peg_count"] = 1
              student_tracker["fail_peg_count"] = 0
           else:
              student_tracker["success_peg_count"] = 0
              student_tracker["fail_peg_count"] = 1
           action = { this_command.get("command")}
           print(crayons.yellow(student_tracker))
           student_tracker_list.append(student_tracker)
           # student_tracker["commands"] = []
           # + = [["command"] = command.get("command"),  ["time"] = command.get("command"), ["result"] = command.get("result")]

        else:
          print(student_tracker_list[index])

