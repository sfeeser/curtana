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
     "Sep 1 16:06:44 bchd.a89b5f49-0b1b-4387-905e-5cf330f8095a student: student@bchd:/home/student$ sudo apt install python3-pip -y [0]"
  
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

def class_name_parse(data: str) -> {}:
    name_parser = re.compile(r'''
        (?P<class_prefix>live-class-id)\s*
        (?P<class_id>.*)
        ''', re.VERBOSE
    )
    class_name_parser_match = name_parser.match(data)
    if class_name_parser_match:
        name_hints = class_name_parser_match.groupdict()  #re function that Returns dicts, keyed by the subgroup name.
    else:
        name_hints = {
        'unparsable': data
        }
    return name_hints

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

def help_parse(data: str) -> {}:
    help_parser = re.compile(r'''
        ^(?P<prefix>\s*(bash)*\s*live-help)\s*
        (?P<lab>[0-9]+)\s*
        (?P<step>[0-9]+)
        ''', re.VERBOSE
    )
    help_parser_match = help_parser.match(data)
    if help_parser_match:
        help_hints = help_parser_match.groupdict()  #re function that Returns dicts, keyed by the subgroup name.
    else:
        help_hints = {
        'unparsable': data
        }
    return help_hints

def clear_help_parse(data: str) -> {}:
    clear_help_parser = re.compile(r'''
        ^(?P<clear>\s*(bash)*\s*live-help\s*clear)
        ''', re.VERBOSE
    )
    clear_help_match = clear_help_parser.match(data)
    if clear_help_match:
        clear_help = clear_help_match.groupdict()  #re function that Returns dicts, keyed by the subgroup name.
    else:
        clear_help = {
        'unparsable': data
        }
    return clear_help

def lab_assignment_parse(data: str) -> {}:
    lab_assignment_parser =  re.compile(r'''
        ^(?P<prefix>\s*(bash)*\s*live-lab)\s*
        (?P<lab>[0-9]+)\s*
        (?P<psswd>student-tracker)\s*
        (?P<class_id>.*)
        ''', re.VERBOSE
    )
    lab_assignment_parser_match = lab_assignment_parser.match(data)  
    if lab_assignment_parser_match:
        this_lab_assignment = lab_assignment_parser_match.groupdict()
    else:
        this_lab_assignment = {
        'unparsable': data
        }
    return this_lab_assignment

def live_gtg_parse(data: str) -> {}:
    live_gtg_parser =  re.compile(r'''
        ^(?P<prefix>\s*(bash)*\s*live-gtg)\s*
        (?P<lab>[0-9]+)\s*
        ''', re.VERBOSE
    )
    live_gtg_parser_match = live_gtg_parser.match(data)
    if live_gtg_parser_match:
        live_gtg_lab = live_gtg_parser_match.groupdict()
    else:
        live_gtg_lab = { 'unparsable': data }
    return live_gtg_lab


def thinktime(start_time):
    # start time

    # convert time string to datetime
    t1 = datetime.strptime(start_time, "%Y:%b:%d:%H:%M:%S")

    # get difference
    delta = datetime.utcnow() - t1
    return delta.total_seconds()

"""
Data - Two distict data structures are maintained

# A set of dictionaries per student
student_tracker_list:
  - domain: string
    class_id: string
    student_name: string
    cmd_peg_count: int
    success_peg_count: int
    fail_peg_count: int
    time_stamp: string
    latest_command: string
    latest_result: string
    live_help: string
    live_gtg: string 

# A stand-alone stucture used to allow the instructor to set a lab assisgnment to a specific class
lab_assignment:
    lab: string
    class_id: string
"""

def init_student_tracker(student_tracker_list,class_id):
    for i in range(len(student_tracker_list)):
        if student_tracker_list[i]["class_id"] == class_id:
             student_tracker_list[i]["cmd_peg_count"] = 0
             student_tracker_list[i]["success_peg_count"] = 0
             student_tracker_list[i]["fail_peg_count"] = 0
             student_tracker_list[i]["live_help"] = ""
             student_tracker_list[i]["live_gtg"] = ""
    return student_tracker_list


def parse_logs(filename):
    student_tracker = {}
    student_tracker_list = []
    verbose = False
    lab_assignment = {}
    gtg_counter = 0
    
    with open(filename, "r") as logfile:
        commands = logfile.readlines()
        for command in commands:
            this_command = parse(command)
            # The next line is a generator, it will return the idex of an existing student record, else "Init_me"
            index = next((i for i, item in enumerate(student_tracker_list) if item["domain"] == this_command.get('domain')), "Init_me")
            if index == "Init_me":
               student_tracker = {}
               student_tracker["domain"] = this_command.get('domain')
               student_tracker["student_name"] = ""
               student_tracker["cmd_peg_count"] = 0
               student_tracker["success_peg_count"] = 0
               student_tracker["fail_peg_count"] = 0
               student_tracker["lab_gtg"] = "0"
               student_tracker["class_id"] = ""
               student_tracker_list.append(student_tracker)
               # refreesh the index just created onw NOT called "Init_me"
               index = next((i for i, item in enumerate(student_tracker_list) if item["domain"] == this_command.get('domain')), "Init_me")
            # update the student tracker array based on this log entry
            student_tracker_list[index]["cmd_peg_count"] += 1
            # increment sucess/fail peg count based on bash result code
            if this_command.get("result") == "0":
                student_tracker_list[index]["success_peg_count"] += 1
            else:
                student_tracker_list[index]["fail_peg_count"] += 1
            # overwrite the latest command with current command
            student_tracker_list[index]["latest_command"] = this_command.get('command')
            # overwrite the lastest bash result code
            student_tracker_list[index]["latest_result"]  = this_command.get('result')
            # PARSE command for class name, overwrite class-id if present
            class_name_check = class_name_parse(this_command.get("command"))
            if "class_id" in class_name_check:
                  student_tracker_list[index]["class_id"] = class_name_check.get("class_id")
            # PARSE command for student name, overwrite student name if present
            name_check = name_parse(this_command.get("command"))
            if "name" in name_check:
                  student_tracker_list[index]["student_name"] = name_check.get("name")
            # PARSE command for SETUP message
            # Store the time/date string in a python datetime friendly manner
            student_tracker_list[index]["time_stamp"] = "2022" \
              + ":" + this_command.get('month') \
              + ":" + this_command.get('day') \
              + ":" + this_command.get('hour') \
              + ":" + this_command.get('minute') \
              + ":" + this_command.get('second')
            # obe-wan kenobi you're my only hope
            help_check = help_parse(this_command.get("command"))
            if "step" in help_check:
                  student_tracker_list[index]["help_request"] = help_check.get("lab") + "-" + help_check.get("step")
            # obe-wan, I do NOT need your help anymore.
            clear_help = clear_help_parse(this_command.get("command"))
            if "clear" in clear_help:
                  student_tracker_list[index]["help_request"] = ""
            # Instructor incantation to enter lab assignment
            new_lab_assignment = lab_assignment_parse(this_command.get("command"))
            if "lab" in new_lab_assignment:
                lab_assignment = new_lab_assignment
                init_student_tracker(student_tracker_list,lab_assignment.get("class_id"))    
            #Student reports assigned lab is completed
            lab_gtg = live_gtg_parse(this_command.get("command"))
            if "lab" in lab_gtg:
                student_tracker_list[index]["lab_gtg"] = lab_gtg.get("lab")
    return student_tracker_list, lab_assignment


def gtg_calc(student_tracker_list, lab_assignment):
    gtg_counter = 0
    #Count GTG for labs matching the assignment
    for student in student_tracker_list:
        if student["lab_gtg"] >= lab_assignment.get('lab'):
            if student["class_id"] == lab_assignment.get('class_id'):
                gtg_counter += 1
    return gtg_counter            


def output_data(student_tracker_list, lab_assignment, gtg_counter):
    print(crayons.yellow(f"\nLab Counter only counting students assigned to: {lab_assignment.get('class_id')}")) 
    print(crayons.yellow(f"Lab Assignment: {lab_assignment.get('lab')}  COUNTER: {gtg_counter}"))
    print(crayons.green(f"Time now: {datetime.now().isoformat(' ', 'seconds')}")) 
    
    print(crayons.green(f"                                                Suc-             Last Command "))
    print(crayons.green(f"Class-ID          Student           Help  Cmds  cess  Fail  GTG   Timestamp      Seconds  Results + Latest Command"))
    print(crayons.green(f"----------------- ----------------  ----- ----  ----  ----  ---  --------------  -------  ----------------------------------"))
    for student in student_tracker_list:
        print(crayons.green(f"{student.get('class_id','NONE'):<18}"), end = '')
        print(crayons.green(f"{student.get('student_name','none'):<17}"), end = '')
        print(crayons.red  (f"{student.get('help_request',''):>5}"), end = '')
        print(crayons.green(f"{student.get('cmd_peg_count'):>6}  "), end = '')
        print(crayons.green(f"{student.get('success_peg_count'):>4}  "), end = '')
        print(crayons.green(f"{student.get('fail_peg_count'):>4}" ), end = '')
        print(crayons.green(f"{student.get('lab_gtg',''):>5}" ), end = '')
        print(crayons.yellow(f"{student.get('time_stamp')[-14:]:>16}  "), end = '')
        sluggy = int(thinktime(student.get('time_stamp')))
        if sluggy < 120:
           print(crayons.green(f" {sluggy:>6}  "), end = '')
        elif sluggy < 300:
           print(crayons.yellow(f" {sluggy:>6}  "), end = '')
        elif sluggy >= 300:
           print(crayons.red(f" {sluggy:>6}  "), end = '')
        if student.get('latest_result') is None:
            print(crayons.green(f"{[  0]}"), end = '' )
        else:
            print(crayons.green(f"[{student.get('latest_result'):>3}]"), end = '' )
        print(crayons.green(f" {str(student.get('latest_command')):>3}"))

if os.path.exists("/var/log/students.log"):
    file_name = "/var/log/students.log"
else:
    file_name = "students.log"


while (True):
    student_tracker_list, lab_assignment = parse_logs(file_name)
    gtg_counter = gtg_calc(student_tracker_list, lab_assignment)
    os.system('clear')
    output_data(student_tracker_list, lab_assignment, gtg_counter)
    student_tracker_list = {}
    lab_assignment = {}
    gtg_counter = 0
    time.sleep(2)
