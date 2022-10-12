import time
import os
from subprocess import call
import json
import crayons
import re
from datetime import datetime
from operator import itemgetter, attrgetter
from jinja2 import Environment, FileSystemLoader

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
        (?P<host>[a-z0-9]*)\.\s*
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
        (?P<class_id>[0-9a-zA-Z-]*)\s*
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
        "*(?P<name>[a-zA-Z0-9 ]*)"*
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
        (?P<class_id>[0-9a-zA-Z-]*)\s*
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
    # convert time string to datetime
    t1 = datetime.strptime(start_time, "%Y:%b:%d:%H:%M:%S")
    # get difference
    delta = datetime.utcnow() - t1
    secs = delta.total_seconds()
    if secs > 432000:
        return "HDJ"
    elif secs > 345600:
        return ">4 Days"
    elif secs > 259200:
        return ">3 days"
    elif secs > 172800:
        return ">2 days"
    elif secs >= 86400:
        return ">1 day"
    elif secs < 86400:
        hour = secs // 3600
        secs %= 3600
        minutes = secs // 60
        secs %= 60
        return "%d:%02d:%02d" % (hour, minutes, secs)

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
 -  lab_assignment: int
    class_id: string
"""

def init_student_tracker(student_tracker_list,class_id):
    # [student["cmd_peg_count"] = 0 for student in student_tracker_list if student["class_id"] == class_id]
    for i in range(len(student_tracker_list)):
        if student_tracker_list[i]["class_id"] == class_id:
             student_tracker_list[i]["cmd_peg_count"] = 0
             student_tracker_list[i]["success_peg_count"] = 0
             student_tracker_list[i]["fail_peg_count"] = 0
             student_tracker_list[i]["help_request"] = ''
             student_tracker_list[i]["lab_gtg"] = 0 
    return student_tracker_list


def parse_logs(filename):
    student_tracker = {}
    student_tracker_list = []
    verbose = False
    lab_assignments = []
    class_tracker_list = []
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
               student_tracker["lab_gtg"] = 0
               student_tracker["class_id"] = ""
               student_tracker_list.append(student_tracker)
               # refresh the index just created onw NOT called "Init_me"
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
                  student_tracker_list[index]["student_name"] = name_check.get("name").lower()
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
                print("PARSE")
                print(new_lab_assignment)
                lab_index = next((i for i, item in enumerate(lab_assignments) if item["class_id"] == new_lab_assignment.get('class_id')), -1)
                print(lab_index)
                print(new_lab_assignment.get("class_id"))
                if lab_index == -1:
                   lab_tracker = {}
                   lab_tracker["class_id"] = new_lab_assignment.get("class_id")
                   lab_tracker["lab"] = new_lab_assignment.get("lab")
                   lab_assignments.append(lab_tracker)
                   lab_index = next((i for i, item in enumerate(lab_assignments) if item["class_id"] == new_lab_assignment.get("class_id")), 0)
                lab_assignments[lab_index]["class_id"] = new_lab_assignment.get("class_id")
                lab_assignments[lab_index]["lab"] = new_lab_assignment.get("lab")                
                print(f"lab assignments >{lab_assignments[lab_index]['class_id']}<")
                print(lab_assignments)
                init_student_tracker(student_tracker_list,new_lab_assignment.get("class_id"))    
                student_tracker_list[index]["latest_command"] = "NEW LAB ASSIGNED!"
            #Student reports assigned lab is completed
            lab_gtg = live_gtg_parse(this_command.get("command"))
            if "lab" in lab_gtg:
                student_tracker_list[index]["lab_gtg"] = int(lab_gtg.get("lab"))
    return student_tracker_list, lab_assignments


def gtg_calc(students, lab_assignment):
    gtg_counter = 0
    #Count GTG for labs matching the assignment
    for student in students:
        if student["lab_gtg"] == lab_assignment:
            gtg_counter += 1
    return gtg_counter            

def sort_students(student_tracker_list):
    s   = sorted(student_tracker_list, key=itemgetter('student_name')) 
    ss  = sorted(s,   key=itemgetter('lab_gtg'))
    sss = sorted(ss, key=itemgetter('class_id'))
    return sss

def write_page(page_name, template_name, student_tracker_list, lab, id, gtg_counter):
     file_loader = FileSystemLoader('templates')
     env = Environment(loader=file_loader)
     tm = env.get_template(template_name)
     page = tm.render(gtg_counter=gtg_counter,student_tracker_list=student_tracker_list,lab=lab, id=id)
     #TODO: The next line MUST point to where the web page is served until it is served from curtana natively (flask).
     f = open("/opt/enchilada/run/static/curtana/" + page_name, "w")     
     # f = open(page_name, "w")     
     f.write(page)
     f.close


def write_class_pages(student_tracker_list,lab_assignments):
    class_ids = []
    for student in student_tracker_list:
        if student['class_id'] not in class_ids:
            class_ids.append(student['class_id'])
            this_id_list = [classmate for classmate in student_tracker_list if classmate['class_id'] == student['class_id']]
            this_lab_assignment = [assignment for assignment in lab_assignments if assignment['class_id'] == student['class_id']]
            # Handle undefined pab assignment
            if this_lab_assignment == []:
                 this_lab_assignment = [{'class_id': student['class_id'], 'lab': 0}]
            id = this_lab_assignment[0].get('class_id')
            lab = this_lab_assignment[0].get('lab')
            gtg_counter = gtg_calc(this_id_list, lab)
            write_page(student.get('class_id') + "%s.html", "index.j2", this_id_list, lab, id, gtg_counter)


def output_data(student_tracker_list, lab_assignment):
    print(crayons.green(f"Time now: {datetime.now().isoformat(' ', 'seconds')}")) 
  
    print(crayons.green(f"                                                 Suc-             Last Command "))
    print(crayons.green(f"Class-ID        Student              Help  Cmds  cess  Fail  GTG   Timestamp      Seconds  Results + Latest Command"))
    print(crayons.green(f"--------------  ------------------   ----- ----  ----  ----  ---  --------------  -------  ----------------------------------"))
    for student in student_tracker_list:
        print(crayons.green(f"{student.get('class_id','NONE'):<16}"), end = '')
        print(crayons.green(f"{student.get('student_name','none'):<20}"), end = '')
        print(crayons.red  (f"{student.get('help_request',''):>5}"), end = '')
        print(crayons.green(f"{student.get('cmd_peg_count'):>6}  "), end = '')
        print(crayons.green(f"{student.get('success_peg_count'):>4}  "), end = '')
        print(crayons.green(f"{student.get('fail_peg_count'):>4}" ), end = '')
        print(crayons.green(f"{student.get('lab_gtg',''):>5}" ), end = '')
        print(crayons.yellow(f"{student.get('time_stamp')[-14:]:>16}  "), end = '')
        think_lag = thinktime(student.get('time_stamp'))
        student['think_lag'] = think_lag
        print(crayons.red(f" {think_lag:>6}  "), end = '')
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
    student_tracker_list, lab_assignments = parse_logs(file_name)
    os.system('clear')
    student_tracker_list = sort_students(student_tracker_list)
    output_data(student_tracker_list, lab_assignments)
    write_page("tracker.html", "index.j2", student_tracker_list,0,0,0)
    write_class_pages(student_tracker_list,lab_assignments)    
    student_tracker_list = {}
    lab_assignment = {}
    gtg_counter = 0
    time.sleep(2)
